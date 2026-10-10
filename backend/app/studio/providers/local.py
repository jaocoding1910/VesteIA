"""Provedores preservados da versão 1.5.8: foto como avatar, CatVTON local,
Google Vertex Virtual Try-On e o gerador local de avatar por selfie."""
from __future__ import annotations

import base64

from app.studio.images import data_url, decode_base64_image, fit_canvas, to_jpeg
from app.studio.providers.base import (AvatarRequest, Capabilities, Generated, ProviderError, SizePreviewRequest,
                                       TryOnRequest)

# Tradução das regiões do VesteIA para as categorias aceitas pelo serviço legado.
LEGACY_CATEGORY = {"upper": "camiseta", "outer": "jaqueta", "lower": "calca", "full": "vestido"}


def _decode_data_url(value: str):
    if not isinstance(value, str) or "," not in value:
        raise ProviderError("O serviço devolveu uma resposta inconclusiva.", 502, sent=True, inconclusive=True)
    return decode_base64_image(value.split(",", 1)[1])


class PhotoAvatarProvider:
    """Usa a própria foto de corpo inteiro como avatar base. Sem IA e sem custo."""

    def capabilities(self) -> Capabilities:
        return Capabilities(id="photo", label="Sua foto como avatar (sem IA)", kind="none", paid=False, ready=True,
                            message="A foto de corpo inteiro é centralizada em formato retrato, sem distorção e sem gerar regiões.",
                            generates=False, accepts_partial_photo=False)

    def planned_calls(self, request: AvatarRequest) -> int:
        return 0

    def generate_avatar(self, request: AvatarRequest) -> Generated:
        if request.framing != "corpo_inteiro":
            raise ProviderError("Sem um gerador de IA configurado, o avatar base exige uma foto de corpo inteiro. "
                                "Envie uma foto em pé, de frente, da cabeça aos pés.", 422)
        return Generated(fit_canvas(request.photo), "photo", None, False, 0,
                         ["Avatar base = sua foto original, apenas centralizada. Nenhuma região foi gerada."])


class LegacyTryOnProvider:
    """CatVTON local ou Google Vertex, pelo código existente em app.services.tryon_service."""

    def __init__(self, provider: str):
        self.provider = provider

    def capabilities(self) -> Capabilities:
        from app.services import tryon_service
        config = tryon_service.configuration()
        if self.provider == "catvton":
            ready = config.get("provider") == "catvton" and tryon_service.local_status(config)
            return Capabilities(id="catvton", label="CatVTON local", kind="local", paid=False, ready=ready,
                                message="CatVTON pronto neste computador." if ready else
                                "CatVTON local indisponível. Defina TRYON_ENABLED=true e abra INICIAR_IA_LOCAL.bat.",
                                model="CatVTON", multi_garment=False, size_previews=False)
        ready = config.get("provider") == "google-vertex" and config.get("configured", False)
        return Capabilities(id="google-vertex", label="Google Vertex Virtual Try-On", kind="external", paid=True,
                            ready=ready, message="Configurado." if ready else "Não configurado. Consulte backend/ATIVAR_IA.md.",
                            model=config.get("model"), multi_garment=False, size_previews=False)

    def planned_calls(self, request: TryOnRequest) -> int:
        return len(request.garments)

    def try_on(self, request: TryOnRequest) -> Generated:
        from app.services import tryon_service
        current = request.base
        calls = 0
        for garment in request.garments:
            try:
                calls += 1
                result = tryon_service.generate(to_jpeg(current), to_jpeg(garment.image), LEGACY_CATEGORY[garment.slot])
            except tryon_service.TryOnError as error:
                # Conservador: só devolve a cota quando com certeza nada foi enviado (configuração/conexão).
                raise ProviderError(error.message, error.status if error.status in (413, 422, 429, 503) else 502,
                                    sent=calls > 1 or error.status not in (413, 503)) from error
            current = _decode_data_url(result.get("image"))
        notes = ["Peças aplicadas uma por vez a partir do avatar base aprovado."] if len(request.garments) > 1 else []
        return Generated(current, self.provider, self.capabilities().model, False, calls, notes)

    def size_preview(self, request: SizePreviewRequest) -> Generated:
        raise ProviderError("Este provedor não recebe medidas: não consegue gerar diferenças confiáveis por tamanho. "
                            "Use a comparação de medidas.", 422)


class LocalSelfieAvatarProvider:
    """Gerador local experimental (integracao/avatar). Aceito somente quando expande a própria foto."""

    def capabilities(self) -> Capabilities:
        from app.services.selfie_avatar import avatar_status
        status = avatar_status()
        return Capabilities(id="local", label="Gerador local de avatar (experimental)", kind="local", paid=False,
                            ready=bool(status.get("configured")), message=status.get("message", ""), model="IP-Adapter local")

    def planned_calls(self, request: AvatarRequest) -> int:
        return 1

    def generate_avatar(self, request: AvatarRequest) -> Generated:
        from app.services.selfie_avatar import generate_avatar
        from app.services.tryon_service import TryOnError
        try:
            result = generate_avatar(to_jpeg(request.photo), request.body_reference or "masculino")
        except TryOnError as error:
            raise ProviderError(error.message, error.status, sent=error.status != 503) from error
        if result.get("body_source") != "photo_outpaint":
            raise ProviderError("O gerador local usou um corpo de modelo fixo em vez de expandir sua foto. "
                                "O resultado foi descartado para não colar seu rosto em outro corpo.", 422, sent=True)
        return Generated(_decode_data_url(result.get("image")), "local", "IP-Adapter local", False, 1,
                         [result.get("message", "Regiões fora da foto foram estimadas.")])


def b64_of(image) -> str:
    return base64.b64encode(to_jpeg(image)).decode("ascii")


__all__ = ["PhotoAvatarProvider", "LegacyTryOnProvider", "LocalSelfieAvatarProvider", "data_url"]
