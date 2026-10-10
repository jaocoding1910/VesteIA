"""Expansão experimental de foto. Não reconstrói medidas ocultas do corpo.

Mantém o conteúdo fotografado (incluindo parte do fundo) e gera fora dele.
Executado no subprocesso já usado pelo servidor; nenhuma foto vai ao disco.
"""
import base64
import io
import json
import sys
from pathlib import Path
from contextlib import redirect_stdout
from PIL import Image, ImageOps
import cv2
import numpy as np

MODEL = "stable-diffusion-v1-5/stable-diffusion-inpainting"
ADAPTER = "h94/IP-Adapter"
ROOT = Path(__file__).resolve().parent
SIZE = (512, 768)


def decode(value):
    if not isinstance(value, str):
        raise ValueError("Imagem inválida.")
    raw = base64.b64decode(value, validate=True)
    if len(raw) > 7 * 1024 * 1024:
        raise ValueError("Envie uma foto de até 7 MB.")
    with Image.open(io.BytesIO(raw)) as image:
        if (image.format not in {"JPEG", "PNG", "WEBP"}
                or min(image.size) < 128
                or image.width * image.height > 16_000_000):
            raise ValueError("Use JPG, PNG ou WebP com pelo menos 128 pixels por lado.")
        return ImageOps.exif_transpose(image).convert("RGB")


def face_box(image):
    smaller = image.copy()
    smaller.thumbnail((1200, 1200))
    gray = cv2.cvtColor(np.asarray(smaller), cv2.COLOR_RGB2GRAY)
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    boxes = detector.detectMultiScale(gray, scaleFactor=1.08,
                                     minNeighbors=5, minSize=(35, 35))
    if len(boxes) != 1:
        raise ValueError("Use uma foto frontal, bem iluminada, com um único rosto visível. Este detector ainda pode falhar com perfis ou rostos pequenos.")
    sx, sy = image.width / smaller.width, image.height / smaller.height
    x, y, w, h = boxes[0]
    return round(x*sx), round(y*sy), round(w*sx), round(h*sy)


def prepare_photo(image, face):
    """Transformação uniforme: nunca estica, nunca corta a foto enviada.

    A máscara permite modificar apenas uma estreita borda de transição e
    a região fora da foto. O rosto e o interior do tronco ficam protegidos.
    """
    width, height = SIZE
    x, y, w, h = face
    scale = min(68 / w, (width-24) / image.width,
                (height-48) / image.height)
    resized = image.resize((max(1, round(image.width*scale)),
                            max(1, round(image.height*scale))),
                           Image.Resampling.LANCZOS)
    left = round(width/2 - (x+w/2)*scale)
    top = round(84 - y*scale)
    left = max(12, min(left, width-12-resized.width))
    top = max(12, min(top, height-24-resized.height))
    canvas = Image.new("RGB", SIZE, (210, 210, 210))
    canvas.paste(resized, (left, top))

    # Feather para dentro da foto: não reutiliza pixels do fundo cinza fora dela.
    yy, xx = np.mgrid[:resized.height, :resized.width]
    distance = np.minimum.reduce((xx, yy, resized.width-1-xx,
                                  resized.height-1-yy))
    keep = np.clip(distance / 8, 0, 1) * 255
    # Garante proteção integral do rosto mesmo perto da borda do enquadramento.
    fx, fy = round(x*scale), round(y*scale)
    fw, fh = max(1, round(w*scale)), max(1, round(h*scale))
    keep[fy:min(resized.height, fy+fh), fx:min(resized.width, fx+fw)] = 255
    alpha = Image.new("L", SIZE, 0)
    alpha.paste(Image.fromarray(keep.astype(np.uint8)), (left, top))
    mask = ImageOps.invert(alpha)
    reference = image.crop((max(0, round(x-w*.3)), max(0, round(y-h*.55)),
                            min(image.width, round(x+w*1.3)),
                            min(image.height, round(y+h*1.2))))
    return canvas, mask, reference


def load_pipeline(allow_download=False):
    import torch
    from diffusers import StableDiffusionInpaintPipeline, DDIMScheduler
    if not torch.cuda.is_available():
        raise ValueError("Este teste requer a GPU NVIDIA com CUDA.")
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        MODEL, torch_dtype=torch.float16, low_cpu_mem_usage=True,
        local_files_only=not allow_download)
    pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
    pipe.load_ip_adapter(ADAPTER, subfolder="models",
                         weight_name="ip-adapter-plus-face_sd15.safetensors",
                         local_files_only=not allow_download)
    pipe.set_ip_adapter_scale(0.65)
    pipe.enable_model_cpu_offload()
    pipe.enable_vae_slicing()
    return pipe


def generate(data):
    import torch
    kind = data.get("template")
    if kind not in {"masculino", "feminino"}:
        raise ValueError("Seleção de apresentação inválida.")
    photo = decode(data["selfie"])
    canvas, mask, reference = prepare_photo(photo, face_box(photo))
    person = "adult man" if kind == "masculino" else "adult woman"
    prompt = (
        f"photorealistic full length photograph of exactly one {person}, "
        "extend the existing photograph below and around the same person, "
        "one continuous anatomically coherent body, natural proportions, "
        "match existing visible skin and lighting, continue existing visible "
        "clothing, standing upright, arms relaxed, natural hands, dark trousers, "
        "simple shoes, both feet visible, coherent background, realistic fabric. "
        "If only the face is visible use a plain neutral t-shirt. "
        + ("If a bare male torso is already visible continue that torso without covering it."
           if kind == "masculino" else "Keep unobserved torso covered with neutral clothing.")
    )
    pipe = load_pipeline()
    result = pipe(
        prompt=prompt,
        negative_prompt="cartoon, illustration, plastic skin, distorted, blurry, extra person, duplicate face, extra limbs, missing limbs, disconnected torso, oversized head, text, watermark, nude lower body",
        image=canvas, mask_image=mask, ip_adapter_image=reference,
        width=SIZE[0], height=SIZE[1], num_inference_steps=35,
        guidance_scale=5.0, strength=1.0,
        generator=torch.Generator(device="cpu").manual_seed(44))
    if result.nsfw_content_detected and any(result.nsfw_content_detected):
        raise ValueError("O modelo não retornou uma imagem utilizável. Tente outra foto.")
    generated = result.images[0].convert("RGB")
    # O pipeline pode mudar pixels sem máscara; a composição restaura a fonte.
    output = Image.composite(generated, canvas, mask)
    stream = io.BytesIO()
    output.save(stream, format="JPEG", quality=94)
    return {"image": base64.b64encode(stream.getvalue()).decode("ascii"),
            "body_source": "photo_outpaint", "experimental": True,
            "message": "Foto expandida experimentalmente. O interior da região fotografada foi preservado; corpo fora do enquadramento e suas medidas são estimados. Parte do fundo original permanece."}


if __name__ == "__main__":
    try:
        with redirect_stdout(sys.stderr):
            if "--download" in sys.argv:
                pipe = load_pipeline(allow_download=True)
                (ROOT / "models-ready.txt").write_text(MODEL + "\n" + ADAPTER,
                                                        encoding="utf-8")
                answer = {"ready": True}
            else:
                answer = generate(json.load(sys.stdin))
        print(json.dumps(answer), flush=True)
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"detail": str(error) if isinstance(error, ValueError)
                          else "Falha no modelo. Confira o terminal do avatar; pode faltar memória."}), flush=True)
        sys.exit(1)
