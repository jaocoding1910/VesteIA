"""Provedor SIMULADO para testes sem custo.

Não usa IA. Monta colagens com a própria foto e a imagem da peça e carimba
"SIMULAÇÃO" na imagem, para nunca ser confundido com uma geração real.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat

from app.studio.images import fit_canvas
from app.studio.providers.base import (AvatarRequest, Capabilities, Generated, SizePreviewRequest, TryOnRequest)

REGIONS = {  # (centro x, topo, largura, altura) relativos à tela
    "upper": (0.5, 0.20, 0.44, 0.31),
    "outer": (0.5, 0.19, 0.50, 0.36),
    "lower": (0.5, 0.48, 0.34, 0.42),
    "full": (0.5, 0.20, 0.46, 0.60),
}
WIDTH_KEY = {"upper": "largura_cm", "outer": "largura_cm", "lower": "quadril_cm", "full": "busto_cm"}


_FONT_FILES = ("DejaVuSans-Bold.ttf", "arialbd.ttf", "arial.ttf", "segoeui.ttf", "Arial.ttf", "LiberationSans-Bold.ttf")


def _font(size: int):
    """Fonte com acentos (Windows/Linux); se não houver, usa a padrão e o texto vira ASCII."""
    for name in _FONT_FILES:
        try:
            return ImageFont.truetype(name, size), True
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size), False
    except TypeError:  # Pillow antigo
        return ImageFont.load_default(), False


def _text(draw, xy, text: str, size: int):
    import unicodedata
    font, accents = _font(size)
    if not accents:
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    draw.text(xy, text, fill=(255, 255, 255, 255), font=font, anchor="mm")


def stamp(image: Image.Image, text: str) -> Image.Image:
    out = image.convert("RGB").copy()
    draw = ImageDraw.Draw(out, "RGBA")
    w, h = out.size
    band = max(44, h // 22)
    draw.rectangle([0, 0, w, band], fill=(17, 24, 64, 225))
    _text(draw, (w // 2, band // 2), text, int(band * 0.46))
    draw.rectangle([0, h - band, w, h], fill=(124, 58, 237, 215))
    _text(draw, (w // 2, h - band // 2), "Imagem de teste · não representa caimento real", int(band * 0.38))
    return out


def cutout(garment: Image.Image) -> Image.Image:
    """Separa a peça de um fundo liso (cor dos cantos). Aproximado, só para simulação."""
    rgb = garment.convert("RGB")
    small = ImageOps.contain(rgb, (512, 512))
    w, h = small.size
    corners = [small.getpixel((x, y)) for x, y in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
    bg = tuple(sorted(c[i] for c in corners)[1] for i in range(3))
    diff = Image.new("RGB", small.size, bg)
    from PIL import ImageChops
    delta = ImageChops.difference(small, diff).convert("L")
    mask = delta.point(lambda v: 255 if v > 28 else 0).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    box = mask.getbbox() or (0, 0, w, h)
    piece = small.crop(box).convert("RGBA")
    piece.putalpha(mask.crop(box))
    return piece


def paste_garment(base: Image.Image, garment: Image.Image, slot: str, scale_x: float = 1.0, scale_y: float = 1.0) -> Image.Image:
    out = base.convert("RGB").copy()
    w, h = out.size
    cx, top, rw, rh = REGIONS[slot]
    piece = cutout(garment)
    fitted = ImageOps.contain(piece, (max(8, int(w * rw)), max(8, int(h * rh))), Image.Resampling.LANCZOS)
    # Na simulação de tamanhos, a peça muda na proporção das medidas informadas.
    stretch = fitted.resize((max(8, int(fitted.width * scale_x)), max(8, int(fitted.height * scale_y))), Image.Resampling.LANCZOS)
    x = int(w * cx - stretch.width / 2)
    y = int(h * top)
    shadow = Image.new("RGBA", stretch.size, (0, 0, 0, 0))
    shadow.putalpha(stretch.getchannel("A").point(lambda v: int(v * 0.25)))
    out.paste(Image.new("RGB", stretch.size, (40, 40, 60)), (x + 4, y + 6), shadow)
    out.paste(stretch, (x, y), stretch)
    return out


class MockProvider:
    id = "mock"

    def capabilities(self) -> Capabilities:
        return Capabilities(id="mock", label="Simulação local (sem IA)", kind="simulated", paid=False, ready=True,
                            message="Respostas SIMULADAS para testar o fluxo sem custo. Não representam a qualidade da IA.",
                            model=None, multi_garment=True, size_previews=True)

    def planned_calls(self, request) -> int:
        return 1

    def generate_avatar(self, request: AvatarRequest) -> Generated:
        canvas = fit_canvas(request.photo)
        notes = ["Simulação: a foto foi apenas centralizada, sem gerar corpo."]
        if request.framing != "corpo_inteiro":
            notes.append("Com IA real, as regiões fora da foto seriam estimadas e não representariam medidas reais.")
        return Generated(stamp(canvas, "SIMULAÇÃO · avatar base"), "mock", None, True, 1, notes)

    def try_on(self, request: TryOnRequest) -> Generated:
        image = request.base
        for garment in request.garments:
            image = paste_garment(image, garment.image, garment.slot)
        return Generated(stamp(image, "SIMULAÇÃO · peça aplicada"), "mock", None, True, 1,
                         ["Colagem simulada: não há ajuste ao corpo, sombras ou tecido reais."])

    def size_preview(self, request: SizePreviewRequest) -> Generated:
        key = WIDTH_KEY[request.garment.slot]
        sx = sy = 1.0
        if request.measures.get(key) and request.selected_measures.get(key):
            sx = request.measures[key] / request.selected_measures[key]
        if request.measures.get("comprimento_cm") and request.selected_measures.get("comprimento_cm"):
            sy = request.measures["comprimento_cm"] / request.selected_measures["comprimento_cm"]
        sx, sy = max(0.7, min(1.4, sx)), max(0.7, min(1.4, sy))
        image = paste_garment(request.base, request.garment.image, request.garment.slot, sx, sy)
        return Generated(stamp(image, f"SIMULAÇÃO · tamanho {request.size_label}"), "mock", None, True, 1,
                         ["Escala proporcional às medidas informadas, sem física de tecido."])


def mean_difference(a: Image.Image, b: Image.Image) -> float:
    """Diferença média (0–255) entre duas imagens reduzidas; usada para detectar resultados repetidos."""
    from PIL import ImageChops
    size = (128, 192)
    x = ImageOps.fit(a.convert("L"), size)
    y = ImageOps.fit(b.convert("L"), size)
    return ImageStat.Stat(ImageChops.difference(x, y)).mean[0]
