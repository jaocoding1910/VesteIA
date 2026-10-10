"""Validação e normalização de imagens, somente em memória.

- Aceita JPEG, PNG e WEBP (verifica assinatura e conteúdo, não só a extensão).
- Respeita a orientação EXIF.
- Nunca estica: redimensiona proporcionalmente e completa com margem neutra.
- Remove metadados ao recodificar.
"""
from __future__ import annotations

import base64
import binascii
import io
from dataclasses import dataclass

from PIL import Image, ImageFilter, ImageOps, ImageStat, UnidentifiedImageError

MAX_PIXELS = 40_000_000
ALLOWED = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
CANVAS = (1024, 1536)  # retrato 2:3, mesmo formato das referências
CANVAS_BG = (238, 241, 248)


class ImageValidationError(ValueError):
    def __init__(self, message: str, status: int = 422):
        super().__init__(message)
        self.message = message
        self.status = status


def _signature_ok(raw: bytes) -> bool:
    return raw.startswith(b"\xff\xd8\xff") or raw.startswith(b"\x89PNG\r\n\x1a\n") or (
        raw[:4] == b"RIFF" and raw[8:12] == b"WEBP")


@dataclass
class LoadedImage:
    image: Image.Image  # RGB, orientação corrigida
    original_format: str
    original_size: tuple[int, int]


def load_image(raw: bytes, *, label: str, max_bytes: int, min_side: int = 256) -> LoadedImage:
    if not raw:
        raise ImageValidationError(f"Envie a {label}.", 422)
    if len(raw) > max_bytes:
        raise ImageValidationError(f"A {label} excede {max_bytes // (1024 * 1024)} MB.", 413)
    if not _signature_ok(raw):
        raise ImageValidationError(f"A {label} precisa ser JPEG, PNG ou WEBP.", 415)
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            fmt = probe.format or ""
            if fmt not in ALLOWED:
                raise ImageValidationError(f"A {label} precisa ser JPEG, PNG ou WEBP.", 415)
            if probe.width * probe.height > MAX_PIXELS:
                raise ImageValidationError(f"A {label} tem resolução acima do limite (40 megapixels).", 413)
            probe.load()
            image = ImageOps.exif_transpose(probe)
            if image.mode in ("RGBA", "LA", "P"):
                rgba = image.convert("RGBA")
                flat = Image.new("RGB", rgba.size, (255, 255, 255))
                flat.paste(rgba, mask=rgba.getchannel("A"))
                image = flat
            else:
                image = image.convert("RGB")
    except ImageValidationError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning, SyntaxError) as error:
        raise ImageValidationError(f"Não foi possível ler a {label}. O arquivo pode estar corrompido.", 422) from error
    if min(image.size) < min_side:
        raise ImageValidationError(
            f"A {label} é pequena demais ({image.width}×{image.height}). Use pelo menos {min_side} pixels no menor lado.", 422)
    return LoadedImage(image=image, original_format=fmt, original_size=image.size)


def fit_canvas(image: Image.Image, size: tuple[int, int] = CANVAS, background=CANVAS_BG) -> Image.Image:
    """Redimensiona proporcionalmente e centraliza. Nunca distorce a pessoa."""
    contained = ImageOps.contain(image, size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(contained, ((size[0] - contained.width) // 2, (size[1] - contained.height) // 2))
    return canvas


def limit_size(image: Image.Image, longest: int = 1536) -> Image.Image:
    if max(image.size) <= longest:
        return image
    return ImageOps.contain(image, (longest, longest), Image.Resampling.LANCZOS)


def to_jpeg(image: Image.Image, quality: int = 92) -> bytes:
    out = io.BytesIO()
    image.convert("RGB").save(out, format="JPEG", quality=quality, optimize=True)
    return out.getvalue()


def to_png(image: Image.Image) -> bytes:
    out = io.BytesIO()
    image.save(out, format="PNG", optimize=True)
    return out.getvalue()


def data_url(raw: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def decode_base64_image(b64: str, *, max_bytes: int = 25 * 1024 * 1024) -> Image.Image:
    try:
        raw = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError, TypeError) as error:
        raise ImageValidationError("O provedor devolveu uma imagem inválida.", 502) from error
    loaded = load_image(raw, label="imagem gerada", max_bytes=max_bytes, min_side=64)
    return loaded.image


def quality_warnings(image: Image.Image, *, framing: str) -> list[str]:
    """Avisos objetivos sobre a foto. Não infere medidas nem características do corpo."""
    warnings: list[str] = []
    w, h = image.size
    if min(w, h) < 640:
        warnings.append("Resolução baixa: o rosto e os detalhes podem perder nitidez.")
    small = ImageOps.contain(image, (256, 256)).convert("L")
    brightness = ImageStat.Stat(small).mean[0]
    if brightness < 55:
        warnings.append("A foto está escura. Prefira luz frontal e uniforme.")
    elif brightness > 225:
        warnings.append("A foto está muito clara ou estourada.")
    edges = ImageStat.Stat(small.filter(ImageFilter.FIND_EDGES)).var[0]
    if edges < 60:
        warnings.append("A foto parece desfocada ou com pouco contraste.")
    if framing == "corpo_inteiro" and w > h * 1.05:
        warnings.append("Foto horizontal: para corpo inteiro, uma foto vertical costuma enquadrar melhor.")
    return warnings
