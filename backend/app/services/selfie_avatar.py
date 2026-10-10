"""Avatar experimental local; fotos somente em memória, nunca no catálogo."""
import base64
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from app.services.tryon_service import normalize_image, TryOnError

URL = "http://127.0.0.1:7862"

def avatar_status():
    try:
        with urlopen(URL + "/health", timeout=2) as response:
            data = json.loads(response.read(4096))
        return {"configured": data.get("provider") == "ip-adapter-face-local" and bool(data.get("models_ready")), "models_ready": bool(data.get("models_ready")),
                "message": "Expansão experimental conectada. Confira o rosto, o corpo e a continuidade da foto antes de aprovar." if data.get("models_ready") else "Execute CONFIGURAR_AVATAR_LOCAL.bat para baixar os modelos antes de usar."}
    except (URLError, OSError, ValueError):
        return {"configured": False, "models_ready": False, "message": "Abra INICIAR_AVATAR_LOCAL.bat após configurar o gerador."}

def generate_avatar(selfie, template):
    payload = {"selfie": normalize_image(selfie), "template": template}
    request = Request(URL + "/avatar", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=1200) as response:
            raw = response.read(12 * 1024 * 1024 + 1)
            if len(raw) > 12 * 1024 * 1024: raise TryOnError("Resposta do avatar acima do limite.", 502)
            result = json.loads(raw)
    except HTTPError as error:
        try: detail = json.loads(error.read(4096)).get("detail")
        except (ValueError, OSError): detail = None
        raise TryOnError(detail or "Gerador de avatar indisponível.", error.code if error.code in (409, 422, 429, 503) else 502) from error
    except (URLError, OSError, ValueError) as error:
        raise TryOnError("Sem resposta do gerador. Confira o terminal do avatar.", 503) from error
    try: image = normalize_image(base64.b64decode(result["image"], validate=True))
    except (KeyError, TypeError, ValueError) as error: raise TryOnError("Imagem de avatar inválida.", 502) from error
    return {"image": "data:image/jpeg;base64," + image, "provider": "ip-adapter-face-local", "experimental": True,
            "body_source": "photo_outpaint" if result.get("body_source") == "photo_outpaint" else "template",
            "message": "Foto expandida experimentalmente. A região visível foi preservada com bordas de transição; corpo fora da foto e suas medidas são estimados. Parte do fundo original permanece." if result.get("body_source") == "photo_outpaint" else "Rosto inspirado na selfie. Corpo de referência; não representa medidas inferidas da foto."}
