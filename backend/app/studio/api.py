"""API do provador VesteIA (funciona sem PostgreSQL).

Toda geração exige: sessão válida, consentimento, ação explícita (request_id único),
confirmação do número de gerações (expected_calls) e cota disponível.
Nenhuma imagem é gravada em disco ou banco; nada é repetido automaticamente.
"""
from __future__ import annotations

import json
import logging
import re
import threading
from typing import Callable

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.studio import credits
from app.studio.categories import CATEGORIES, GARMENT_FIELDS, compose_look, slot_of
from app.studio.images import ImageValidationError, data_url, load_image, quality_warnings, to_jpeg
from app.studio.providers import avatar_provider, tryon_provider
from app.studio.providers.base import (AvatarRequest, Capabilities, Generated, GarmentInput, ProviderError,
                                       SizePreviewRequest, TryOnRequest)
from app.studio.providers.mock import mean_difference
from app.studio.sessions import STORE, StudioSession
from app.studio.sizes import BODY_FIELDS, clean_measures, describe_for_prompt, garment_fields
from app.studio.usage import LimitExceeded, get_ledger

log = logging.getLogger("vesteia")
router = APIRouter(prefix="/api/studio", tags=["Provador VesteIA"])
_SLOTS: dict[int, threading.BoundedSemaphore] = {}
_SLOTS_GUARD = threading.Lock()
REQUEST_ID = re.compile(r"[A-Za-z0-9_-]{8,64}")
FRAMINGS = {"rosto", "meio_corpo", "corpo_inteiro"}
UPPER_STATES = {"vestido", "sem_camiseta", "nao_informado"}


def _slots(settings: Settings) -> threading.BoundedSemaphore:
    with _SLOTS_GUARD:
        if settings.max_concurrent not in _SLOTS:
            _SLOTS[settings.max_concurrent] = threading.BoundedSemaphore(settings.max_concurrent)
        return _SLOTS[settings.max_concurrent]


def _session(authorization: str | None) -> StudioSession:
    token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else ""
    session = STORE.get(token)
    if not session:
        raise HTTPException(401, "Sessão expirada ou inválida. Recarregue o provador para iniciar uma nova sessão.")
    return session


def _read(upload: UploadFile | None, *, label: str, settings: Settings, min_side: int = 256):
    if upload is None:
        raise HTTPException(422, f"Envie a {label}.")
    try:
        raw = upload.file.read(settings.max_upload_bytes + 1)
        return load_image(raw, label=label, max_bytes=settings.max_upload_bytes, min_side=min_side).image
    except ImageValidationError as error:
        raise HTTPException(error.status, error.message) from error
    finally:
        upload.file.close()


def _json_field(value: str | None, default, label: str):
    if value in (None, ""):
        return default
    try:
        return json.loads(value)
    except ValueError as error:
        raise HTTPException(422, f"Campo {label} inválido.") from error


def _image_payload(result: Generated) -> dict:
    return {"image": data_url(to_jpeg(result.image, 90)), "provider": result.provider, "model": result.model,
            "simulated": result.simulated, "calls": result.calls, "notes": result.notes,
            "width": result.image.width, "height": result.image.height}


def _guard(session: StudioSession, *, consent: str, request_id: str, caps: Capabilities, planned: int,
           expected_calls: int) -> None:
    if consent != "true":
        raise HTTPException(422, "É preciso autorizar o processamento das imagens antes de gerar.")
    if not caps.ready:
        raise HTTPException(503, caps.message or "Serviço de imagem indisponível.")
    if expected_calls != planned:
        raise HTTPException(409, f"Esta ação solicitará {planned} geração(ões). Confirme novamente com o número atualizado.")
    if not REQUEST_ID.fullmatch(request_id or ""):
        raise HTTPException(422, "Identificador de solicitação inválido.")
    if request_id in session.request_ids:
        raise HTTPException(409, "Solicitação repetida ignorada (clique duplicado). Nenhuma nova geração foi feita.")
    session.request_ids.add(request_id)
    if len(session.request_ids) > 500:
        session.request_ids.pop()


def _run(session: StudioSession, *, settings: Settings, caps: Capabilities, kind: str, planned: int,
         action: Callable[[], dict]) -> dict:
    if not session.lock.acquire(blocking=False):
        raise HTTPException(409, "Já existe uma geração em andamento nesta sessão. Aguarde a conclusão.")
    slots = _slots(settings)
    try:
        if not slots.acquire(blocking=False):
            raise HTTPException(429, "O serviço está ocupado com outra geração. Tente novamente em instantes.")
        ledger = get_ledger(settings)
        try:
            decision = credits.POLICY.authorize(session_id=session.id, provider=caps.id, calls=planned, store_id=None)
            if not decision.allowed:
                raise HTTPException(402, decision.reason)
            try:
                ledger.reserve(settings, paid=caps.paid, session_id=session.id, calls=planned)
            except LimitExceeded as error:
                raise HTTPException(429, error.message) from error
            try:
                payload = action()
            except ProviderError as error:
                refunded = planned if not error.sent else 0
                ledger.release(paid=caps.paid, session_id=session.id, calls=refunded)
                ledger.record(provider=caps.id, kind=kind, calls=planned - refunded,
                              status="inconclusiva" if error.inconclusive else "falha", session_id=session.id)
                log.warning("Geração %s falhou (%s, status %s)", kind, caps.id, error.status)
                raise HTTPException(error.status, {"message": error.message, "inconclusive": error.inconclusive,
                                                   "charged_calls": planned - refunded}) from error
            except ImageValidationError as error:
                ledger.record(provider=caps.id, kind=kind, calls=planned, status="inconclusiva", session_id=session.id)
                raise HTTPException(502, {"message": error.message, "inconclusive": True, "charged_calls": planned}) from error
            used = payload.pop("_calls_used", planned)
            if used < planned:
                ledger.release(paid=caps.paid, session_id=session.id, calls=planned - used)
            ledger.record(provider=caps.id, kind=kind, calls=used, status=payload.get("_status", "ok"), session_id=session.id)
            payload.pop("_status", None)
            credits.POLICY.settle(session_id=session.id, provider=caps.id, calls=used, status="ok", store_id=None)
            payload["usage"] = ledger.snapshot(settings, session.id)
            return payload
        finally:
            slots.release()
    finally:
        session.lock.release()


# ---------------------------------------------------------------------------------------------
@router.get("/status")
def status(authorization: str | None = Header(default=None)):
    settings = get_settings()
    session_id = None
    if authorization:
        found = STORE.get(authorization.removeprefix("Bearer ").strip())
        session_id = found.id if found else None
    return {
        "database_enabled": settings.database_enabled,
        "avatar": avatar_provider(settings).capabilities().public(),
        "tryon": tryon_provider(settings).capabilities().public(),
        "usage": get_ledger(settings).snapshot(settings, session_id),
        "max_upload_mb": settings.max_upload_mb,
        "max_garments": settings.max_garments,
        "max_sizes": settings.max_sizes_per_request,
        "access_code_required": bool(settings.access_code),
        "categories": [{"id": key, "label": value["label"], "slot": value["slot"]} for key, value in CATEGORIES.items()],
        "garment_fields": {slot: [{"id": k, "label": label} for k, label in fields] for slot, fields in GARMENT_FIELDS.items()},
        "privacy": "As fotos são processadas em memória e não são salvas no servidor. Limpar a sessão descarta tudo no navegador.",
    }


@router.post("/session")
def create_session(request: Request, access_code: str = Form(default="")):
    settings = get_settings()
    if settings.access_code and access_code != settings.access_code:
        raise HTTPException(403, "Código de acesso inválido.")
    ledger = get_ledger(settings)
    ip = request.client.host if request.client else "desconhecido"
    if ledger.sessions_from_ip(ip) >= settings.sessions_per_ip_daily:
        raise HTTPException(429, "Muitas sessões criadas hoje a partir desta conexão. Tente amanhã.")
    ledger.count_session_from_ip(ip)
    session = STORE.create(settings.session_ttl_minutes)
    return {"token": session.token, "expires_in_minutes": settings.session_ttl_minutes,
            "usage": ledger.snapshot(settings, session.id)}


@router.delete("/session", status_code=204)
def drop_session(authorization: str | None = Header(default=None)):
    token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else ""
    STORE.drop(token)


@router.post("/photo/check")
def check_photo(photo: UploadFile = File(...), framing: str = Form("corpo_inteiro"),
                authorization: str | None = Header(default=None)):
    """Validação gratuita: formato, tamanho, orientação e avisos de qualidade."""
    _session(authorization)
    settings = get_settings()
    if framing not in FRAMINGS:
        raise HTTPException(422, "Enquadramento inválido.")
    image = _read(photo, label="foto", settings=settings)
    return {"ok": True, "width": image.width, "height": image.height, "warnings": quality_warnings(image, framing=framing)}


@router.post("/avatar")
def create_avatar(photo: UploadFile = File(...), framing: str = Form(...), upper_state: str = Form("nao_informado"),
                  body_reference: str = Form(""), consent: str = Form("false"), request_id: str = Form(""),
                  expected_calls: int = Form(-1), authorization: str | None = Header(default=None)):
    settings = get_settings()
    session = _session(authorization)
    if framing not in FRAMINGS or upper_state not in UPPER_STATES:
        raise HTTPException(422, "Informe o enquadramento da foto e se a parte de cima está vestida.")
    provider = avatar_provider(settings)
    caps = provider.capabilities()
    if framing != "corpo_inteiro" and not caps.accepts_partial_photo:
        raise HTTPException(422, "O modo atual não gera corpo: envie uma foto de corpo inteiro (cabeça aos pés).")
    image = _read(photo, label="foto", settings=settings)
    avatar_request = AvatarRequest(photo=image, framing=framing, upper_state=upper_state,
                                   body_reference=body_reference if body_reference in ("masculino", "feminino") else None)
    planned = provider.planned_calls(avatar_request)
    _guard(session, consent=consent, request_id=request_id, caps=caps, planned=planned, expected_calls=expected_calls)

    def action():
        result = provider.generate_avatar(avatar_request)
        payload = _image_payload(result)
        payload["estimated_regions"] = framing != "corpo_inteiro" and caps.generates
        payload["warnings"] = quality_warnings(image, framing=framing)
        payload["_calls_used"] = result.calls
        return payload

    return _run(session, settings=settings, caps=caps, kind="avatar", planned=planned, action=action)


def _garments(files: list[UploadFile], meta_raw: str, settings: Settings) -> list[GarmentInput]:
    meta = _json_field(meta_raw, [], "garments_meta")
    if not isinstance(meta, list) or not files or len(files) != len(meta):
        raise HTTPException(422, "Envie cada peça com sua categoria.")
    if len(files) > settings.max_garments:
        raise HTTPException(422, f"Envie no máximo {settings.max_garments} peças por geração.")
    categories = []
    for item in meta:
        if not isinstance(item, dict) or item.get("category") not in CATEGORIES:
            raise HTTPException(422, "Escolha uma categoria válida para cada peça.")
        categories.append(item["category"])
    keep = compose_look(categories)
    if len(keep) != len(categories):
        raise HTTPException(422, "Há peças disputando a mesma região do corpo. Mantenha uma peça por região.")
    garments = []
    for index in keep:
        item = meta[index]
        image = _read(files[index], label=f"imagem da peça {index + 1}", settings=settings, min_side=128)
        size = str(item.get("size_label") or "").strip()[:8] or None
        garments.append(GarmentInput(image=image, category=item["category"], slot=slot_of(item["category"]),
                                     description=str(item.get("description") or "")[:160], size_label=size))
    return garments


@router.post("/tryon")
def try_on(base: UploadFile = File(...), garments: list[UploadFile] = File(...), garments_meta: str = Form(...),
           consent: str = Form("false"), request_id: str = Form(""), expected_calls: int = Form(-1),
           authorization: str | None = Header(default=None)):
    settings = get_settings()
    session = _session(authorization)
    provider = tryon_provider(settings)
    caps = provider.capabilities()
    base_image = _read(base, label="imagem do avatar base", settings=settings)
    request = TryOnRequest(base=base_image, garments=_garments(garments, garments_meta, settings))
    planned = provider.planned_calls(request)
    _guard(session, consent=consent, request_id=request_id, caps=caps, planned=planned, expected_calls=expected_calls)

    def action():
        result = provider.try_on(request)
        payload = _image_payload(result)
        payload["garments"] = [{"category": g.category, "slot": g.slot, "size_label": g.size_label} for g in request.garments]
        payload["_calls_used"] = result.calls
        return payload

    return _run(session, settings=settings, caps=caps, kind="tryon", planned=planned, action=action)


@router.post("/size-previews")
def size_previews(base: UploadFile = File(...), garment: UploadFile = File(...), category: str = Form(...),
                  description: str = Form(""), sizes: str = Form(...), selected_label: str = Form(...),
                  body: str = Form("{}"), consent: str = Form("false"), request_id: str = Form(""),
                  expected_calls: int = Form(-1), authorization: str | None = Header(default=None)):
    settings = get_settings()
    session = _session(authorization)
    if category not in CATEGORIES:
        raise HTTPException(422, "Categoria inválida.")
    provider = tryon_provider(settings)
    caps = provider.capabilities()
    if not caps.size_previews:
        raise HTTPException(422, "O provedor atual não consegue gerar diferenças visuais confiáveis por medidas. "
                                 "Use a comparação de medidas.")
    raw_sizes = _json_field(sizes, [], "sizes")
    if not isinstance(raw_sizes, list) or not 2 <= len(raw_sizes) <= settings.max_sizes_per_request:
        raise HTTPException(422, f"Escolha de 2 a {settings.max_sizes_per_request} tamanhos para comparar.")
    fields = garment_fields(category)
    width_field = fields[0]
    parsed = []
    for item in raw_sizes:
        label = str((item or {}).get("label") or "").strip()[:8]
        measures = clean_measures((item or {}).get("measures"), fields)
        if not label:
            raise HTTPException(422, "Tamanho sem nome.")
        if width_field not in measures:
            raise HTTPException(422, f"Faltam medidas da peça no tamanho {label}. Informe ao menos a primeira medida da tabela; "
                                     "não estimamos centímetros pela imagem.")
        parsed.append((label, measures))
    labels = [label for label, _ in parsed]
    if len(set(labels)) != len(labels) or selected_label not in labels:
        raise HTTPException(422, "Tamanhos repetidos ou tamanho escolhido ausente da lista.")
    body_measures = clean_measures(_json_field(body, {}, "body"), BODY_FIELDS)
    selected_measures = dict(parsed)[selected_label]
    base_image = _read(base, label="imagem do avatar base", settings=settings)
    garment_image = _read(garment, label="imagem da peça", settings=settings, min_side=128)
    garment_input = GarmentInput(image=garment_image, category=category, slot=slot_of(category),
                                 description=description[:160])
    planned = len(parsed)
    _guard(session, consent=consent, request_id=request_id, caps=caps, planned=planned, expected_calls=expected_calls)

    def action():
        results, images, error_info = [], [], None
        for label, measures in parsed:
            preview = SizePreviewRequest(base=base_image, garment=garment_input, size_label=label,
                                         selected_label=selected_label, measures=measures,
                                         selected_measures=selected_measures, body=body_measures,
                                         description=describe_for_prompt(category, label, measures, body_measures))
            try:
                generated = provider.size_preview(preview)
            except ProviderError as error:
                if not results:
                    raise
                # Interrompe sem repetir; devolve o que já foi gerado.
                error_info = {"message": error.message, "size": label, "inconclusive": error.inconclusive}
                if error.sent:
                    images.append(None)
                break
            item = _image_payload(generated)
            item["label"] = label
            item["repeated_of"] = next((results[i]["label"] for i, other in enumerate(images)
                                        if other is not None and mean_difference(other, generated.image) < 1.0), None)
            images.append(generated.image)
            results.append(item)
        payload = {"previews": results, "selected_label": selected_label, "illustrative": True,
                   "_calls_used": len(images) if error_info else len(parsed),
                   "_status": "parcial" if error_info else "ok"}
        if error_info:
            payload["error"] = error_info
        return payload

    return _run(session, settings=settings, caps=caps, kind="size_previews", planned=planned, action=action)


@router.get("/usage")
def usage(authorization: str | None = Header(default=None)):
    session = _session(authorization)
    settings = get_settings()
    return get_ledger(settings).snapshot(settings, session.id)


def http_error_handler(_request: Request, exc: HTTPException):
    detail = exc.detail
    body = detail if isinstance(detail, dict) else {"message": str(detail)}
    body.setdefault("inconclusive", False)
    return JSONResponse({"detail": body["message"], **body}, status_code=exc.status_code,
                        headers=getattr(exc, "headers", None))
