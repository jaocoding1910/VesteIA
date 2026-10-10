"""OpenAI Images API (edição com imagens de referência).

Conferido na documentação oficial (out/2026): o modelo `gpt-image-2`
(snapshot `gpt-image-2-2026-04-21`) é aceito em POST /v1/images/edits, que recebe
até 16 imagens de referência; `input_fidelity` NÃO deve ser enviado para gpt-image-2;
`size` aceita WIDTHxHEIGHT múltiplos de 16 (ex.: 1024x1536); a resposta traz `b64_json`.

Regras de custo deste módulo:
- Uma requisição por geração, sem novas tentativas automáticas.
- Só funciona com OPENAI_API_KEY + AI_PAID_ENABLED=true no backend.
- Nenhum corpo de requisição/resposta é registrado em log.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import Settings
from app.studio.categories import CATEGORIES, SLOT_LABEL
from app.studio.images import data_url, decode_base64_image, limit_size, to_jpeg
from app.studio.providers.base import (AvatarRequest, Capabilities, Generated, ProviderError, SizePreviewRequest,
                                       TryOnRequest)

MAX_RESPONSE = 40 * 1024 * 1024
BACKDROP = "seamless very light blue-gray studio backdrop (#EEF1F8) with a soft floor shadow"

IDENTITY = ("Preserve the person's identity exactly: same face and facial features, hairstyle and hair color, facial hair, "
            "skin tone, apparent age and the visible body proportions. Do not beautify, slim, add muscle, change body shape, "
            "height or posture, and do not retouch skin.")
SAFETY = ("Never depict nudity. Any body region that was not visible in the source photo must be covered by plain, "
          "neutral, non-revealing clothing. No logos, brand marks, text or watermarks.")


def _valid_size(value: str) -> bool:
    match = re.fullmatch(r"(\d{3,4})x(\d{3,4})", value)
    if not match:
        return value == "auto"
    w, h = int(match[1]), int(match[2])
    return w % 16 == 0 and h % 16 == 0 and 1 / 3 <= w / h <= 3 and w * h <= 3840 * 2160


def avatar_prompt(request: AvatarRequest) -> str:
    visible = {"rosto": "only the face/head", "meio_corpo": "the upper body", "corpo_inteiro": "the whole body"}[request.framing]
    clothing = ["Keep the clothing that is visible in the photo exactly as it is (same garments, colors and fit)."]
    if request.upper_state == "sem_camiseta" and request.framing != "rosto":
        clothing.append("The person is shirtless in the photo: keep the torso bare, exactly as visible.")
    if request.framing == "rosto":
        clothing.append("The body is not visible: dress it in a plain light-gray crew-neck t-shirt, plain dark-gray "
                        "trousers and plain white sneakers.")
    elif request.framing == "meio_corpo":
        clothing.append("The lower body is not visible: dress it in plain dark-gray trousers and plain white sneakers.")
    estimated = ("" if request.framing == "corpo_inteiro" else
                 "Regions outside the source photo are an estimate: keep them plausible and consistent with the visible "
                 "proportions, without exaggeration. ")
    return (f"Create a photorealistic full-body studio photograph of the SAME real person shown in the reference photo, "
            f"which shows {visible}. {IDENTITY} "
            "Pose and framing: standing upright facing the camera, arms relaxed along the body and slightly away from the "
            "torso, feet slightly apart, entire body visible from the top of the head to the shoes with a small margin, "
            f"centered in a vertical 2:3 frame. Background: {BACKDROP}; soft, even front lighting. "
            f"{' '.join(clothing)} {estimated}{SAFETY}")


def tryon_prompt(request: TryOnRequest) -> str:
    lines = []
    for index, garment in enumerate(request.garments, start=2):
        info = CATEGORIES[garment.category]
        extra = f" ({garment.description.strip()[:160]})" if garment.description.strip() else ""
        size = f", size {garment.size_label}" if garment.size_label else ""
        lines.append(f"- Image {index}: {info['en']}{extra}{size}. Region: {SLOT_LABEL[garment.slot]} — "
                     + ("wear it over the upper-body garment." if garment.slot == "outer" else
                        "it replaces whatever is currently worn on that region (or the bare skin)."))
    return ("Image 1 is the approved base avatar of a real person. The other images are product photos of garments.\n"
            "Edit Image 1 so that the person wears these garments:\n" + "\n".join(lines) + "\n"
            "Keep everything else identical to Image 1: same person, face, hair, skin tone, body shape and proportions, "
            "pose, camera position, framing and crop, background, lighting, and every clothing item not listed above. "
            "Reproduce each garment faithfully from its product photo: exact color, print and graphics, neckline or collar, "
            "sleeve length, fabric texture, seams and details. Fit it naturally on this body with realistic folds, "
            "shadows and arm occlusion. No sticker look, no cut-out edges, no duplicated garments, no remnants of the "
            f"replaced garment. {SAFETY}")


def size_prompt(request: SizePreviewRequest) -> str:
    info = CATEGORIES[request.garment.category]
    return ("Image 1 is the approved base avatar of a real person. Image 2 is a product photo of a "
            f"{info['en']}. Edit Image 1 so the person wears this garment in size {request.size_label}. "
            f"{request.description} For reference, the size the customer selected is {request.selected_label}. "
            "Show the fit (width, length, sleeve and shoulder position, drape) that these measurements imply on this body; "
            "do not change the body to make the garment fit. "
            "Keep the same person, face, body, pose, framing, background and lighting as Image 1, and keep other clothing. "
            f"Reproduce the garment's color, print, collar, sleeves and texture faithfully. {SAFETY}")


class OpenAIImagesProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def capabilities(self) -> Capabilities:
        has_key = bool(os.getenv("OPENAI_API_KEY", "").strip())
        problems = []
        if not has_key:
            problems.append("defina OPENAI_API_KEY no backend/.env")
        if not self.settings.paid_enabled:
            problems.append("confirme o uso pago com AI_PAID_ENABLED=true")
        if not _valid_size(self.settings.openai_size):
            problems.append("OPENAI_IMAGE_SIZE inválido")
        ready = not problems
        return Capabilities(id="openai", label="OpenAI Images", kind="external", paid=True, ready=ready,
                            message=("Pronto. Cada geração é cobrada pela OpenAI na sua conta de API." if ready else
                                     "OpenAI não habilitada: " + "; ".join(problems) + "."),
                            model=self.settings.openai_model, multi_garment=True, size_previews=True)

    def planned_calls(self, request) -> int:
        return 1

    # -- transporte -------------------------------------------------------------------------
    def _post(self, prompt: str, images: list) -> Generated:
        if not self.capabilities().ready:
            raise ProviderError(self.capabilities().message, 503)
        key = os.getenv("OPENAI_API_KEY", "").strip()
        encoded = [to_jpeg(limit_size(image), 90) for image in images[:16]]
        fields = {"model": self.settings.openai_model, "prompt": prompt, "size": self.settings.openai_size,
                  "quality": self.settings.openai_quality, "n": 1, "output_format": "jpeg"}
        transport = os.getenv("OPENAI_EDITS_TRANSPORT", "json").strip().lower()
        if transport == "multipart":
            boundary = "vesteia" + secrets.token_hex(12)
            chunks: list[bytes] = []
            for name, value in fields.items():
                chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
            for index, raw in enumerate(encoded):
                chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="ref{index}.jpg"\r\n'
                              "Content-Type: image/jpeg\r\n\r\n".encode() + raw + b"\r\n")
            chunks.append(f"--{boundary}--\r\n".encode())
            body, content_type = b"".join(chunks), f"multipart/form-data; boundary={boundary}"
        else:
            payload = dict(fields, images=[{"image_url": data_url(raw)} for raw in encoded])
            body, content_type = json.dumps(payload).encode(), "application/json"
        request = Request(f"{self.settings.openai_base_url}/images/edits", data=body, method="POST",
                          headers={"Authorization": f"Bearer {key}", "Content-Type": content_type})
        try:
            with urlopen(request, timeout=self.settings.openai_timeout) as response:
                raw = response.read(MAX_RESPONSE + 1)
        except HTTPError as error:
            raise self._http_error(error) from None
        except (socket.timeout, TimeoutError) as error:
            raise ProviderError("O provedor demorou demais para responder. A chamada pode ter sido cobrada; "
                                "não repetimos automaticamente.", 504, sent=True, inconclusive=True) from error
        except (URLError, OSError) as error:
            raise ProviderError("Não foi possível conectar à OpenAI. Verifique a internet do servidor.", 503) from error
        if len(raw) > MAX_RESPONSE:
            raise ProviderError("Resposta do provedor acima do limite.", 502, sent=True, inconclusive=True)
        try:
            data = json.loads(raw)
            b64 = data["data"][0]["b64_json"]
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise ProviderError("O provedor respondeu sem imagem (resposta inconclusiva). Nenhuma nova tentativa foi feita.",
                                502, sent=True, inconclusive=True) from error
        return Generated(decode_base64_image(b64), "openai", self.settings.openai_model, False, 1)

    @staticmethod
    def _http_error(error: HTTPError) -> ProviderError:
        try:
            info = json.loads(error.read(65536) or b"{}").get("error") or {}
        except (ValueError, OSError):
            info = {}
        code = str(info.get("code") or info.get("type") or "")
        status = error.code
        if status == 400 and "moderation" in code:
            return ProviderError("A solicitação foi recusada pelo filtro de segurança do provedor. "
                                 "Tente outra foto (roupa visível, pose neutra).", 422, sent=True)
        if status == 400:
            return ProviderError("O provedor recusou a solicitação (parâmetros ou imagem). Nada foi gerado.", 422, sent=True)
        if status == 401:
            return ProviderError("Chave da OpenAI inválida ou ausente no backend.", 503)
        if status == 403:
            return ProviderError("A conta OpenAI não tem acesso a este modelo. Pode ser necessária a verificação da organização.", 503)
        if status == 404:
            return ProviderError("Modelo não encontrado. Confira OPENAI_IMAGE_MODEL.", 503)
        if status == 429 and "quota" in code:
            return ProviderError("Sem créditos na conta de API da OpenAI (assinatura do ChatGPT não inclui API).", 503)
        if status == 429:
            return ProviderError("Limite de velocidade do provedor atingido. Aguarde antes de tentar de novo.", 429, sent=True)
        return ProviderError("O provedor não concluiu a geração. Tente mais tarde.", 502, sent=True)

    # -- operações ----------------------------------------------------------------------------
    def generate_avatar(self, request: AvatarRequest) -> Generated:
        result = self._post(avatar_prompt(request), [request.photo])
        if request.framing != "corpo_inteiro":
            result.notes.append("Partes do corpo fora da foto foram estimadas pela IA e não representam medidas reais.")
        return result

    def try_on(self, request: TryOnRequest) -> Generated:
        return self._post(tryon_prompt(request), [request.base] + [g.image for g in request.garments])

    def size_preview(self, request: SizePreviewRequest) -> Generated:
        result = self._post(size_prompt(request), [request.base, request.garment.image])
        result.notes.append("Prévia ilustrativa orientada por medidas; não é simulação física validada.")
        return result
