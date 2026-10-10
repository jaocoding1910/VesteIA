"""Local VesteIA bridge. Copy beside official CatVTON app.py; uses its existing models.
Does not call submit_function, save photos, or start a Gradio/public tunnel.
"""
import base64
import io
import json
import logging
import os
import html
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import BoundedSemaphore
from PIL import Image, ImageOps, ImageFilter

MAX_BODY = 22 * 1024 * 1024
LOCK = BoundedSemaphore(1)
ENGINE = None
DIAGNOSTICO = None
CONFIG_PATH = Path(os.environ.get('VESTEIA_AJUSTES', str(Path(__file__).with_name('ajustes_ia.json'))))
DEFAULTS = {'steps': 50, 'guidance': 2.5, 'seed': 42, 'blur': 5, 'upper_cleanup': 3}


def settings():
    config = DEFAULTS.copy()
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding='utf-8-sig'))
            if not isinstance(data, dict):
                raise ValueError('expected object')
            config.update({k: v for k, v in data.items() if k in config})
        for key, lo, hi in [('steps', 10, 80), ('seed', 0, 2147483647), ('blur', 0, 15), ('upper_cleanup', 0, 7)]:
            value = config[key]
            if type(value) is not int or not lo <= value <= hi:
                raise ValueError(key)
        if type(config['guidance']) not in (int, float) or not 1 <= config['guidance'] <= 5:
            raise ValueError('guidance')
        if config['upper_cleanup'] not in (0, 3, 5, 7):
            raise ValueError('upper_cleanup must be 0, 3, 5 or 7')
        return config
    except (OSError, ValueError, TypeError):
        logging.warning('Arquivo de ajustes invalido; usando valores padrao.')
        return DEFAULTS.copy()


def clean_mask(mask, category, config):
    mask = mask.convert('L')
    size = config['upper_cleanup']
    if category == 'upper' and size:
        # Opening removes thin protrusions; avoids a fixed body/arm crop.
        mask = mask.filter(ImageFilter.MinFilter(size)).filter(ImageFilter.MaxFilter(size))
    return mask


def encode_image(image):
    output = io.BytesIO()
    image.convert('RGB').save(output, format='JPEG', quality=94)
    return base64.b64encode(output.getvalue()).decode('ascii')



def decode_image(value):
    raw = base64.b64decode(value, validate=True)
    if len(raw) > 7 * 1024 * 1024:
        raise ValueError('image too large')
    with Image.open(io.BytesIO(raw)) as image:
        if image.format not in {'JPEG', 'PNG', 'WEBP'} or min(image.size) < 128 or image.width * image.height > 16_000_000:
            raise ValueError('invalid image')
        return ImageOps.exif_transpose(image).convert('RGB')


def infer(data):
    global DIAGNOSTICO
    config = settings()
    category = data['category']
    if category not in {'upper', 'lower', 'overall'}:
        raise ValueError('invalid category')
    person = decode_image(data['person'])
    garment = decode_image(data['garment'])
    e = ENGINE
    person = e.resize_and_padding(person, (e.args.width, e.args.height))
    garment = e.resize_and_padding(garment, (e.args.width, e.args.height))
    original_mask = e.automasker(person, category)['mask'].convert('L')
    mask = clean_mask(original_mask, category, config)
    if config['blur']:
        mask = e.mask_processor.blur(mask, blur_factor=config['blur']).convert('L')
    with e.torch.inference_mode():
        result = e.pipeline(
            image=person, condition_image=garment, mask=mask,
            width=person.width, height=person.height,
            num_inference_steps=config['steps'], guidance_scale=config['guidance'],
            generator=e.torch.Generator(device='cuda').manual_seed(config['seed'])
        )[0]
    # Keep face, background and body pixels outside the garment mask unchanged.
    generated = result.convert('RGB')
    result = Image.composite(generated, person, mask.convert('L'))
    tint = Image.blend(person, Image.new('RGB', person.size, (255, 45, 65)), 0.45)
    overlay = Image.composite(tint, person, mask.convert('L'))
    encoded = encode_image(result)
    DIAGNOSTICO = (config.copy(), tuple((title, encode_image(image)) for title, image in [
        ('Pessoa usada', person), ('Peca usada', garment),
        ('Mascara original', original_mask), ('Mascara ajustada', mask),
        ('Area de aplicacao', overlay), ('Antes da composicao', generated),
        ('Resultado final', result)]))
    print('Geracao concluida com ajustes: ' + json.dumps(config), flush=True)
    return {'image': encoded, 'provider': 'catvton'}


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(30)

    def reply(self, status, value):
        payload = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        if self.path == '/diagnostico':
            snapshot = DIAGNOSTICO
            if snapshot is None:
                content = '<p>Gere uma previa no VesteIA e atualize esta pagina.</p>'
            else:
                config, cards = snapshot
                content = '<p>Ajustes usados: ' + html.escape(json.dumps(config)) + '</p><main>'
                content += ''.join('<figure><figcaption>' + title + '</figcaption><img src="data:image/jpeg;base64,' + image + '"></figure>' for title, image in cards)
                content += '</main>'
            page = ('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Diagnostico VesteIA</title><style>body{background:#121722;color:#eef2ff;font-family:Arial;padding:20px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:15px}figure{margin:0;padding:12px;background:#202838;border-radius:12px}img{width:100%;margin-top:12px}p{line-height:1.5}</style><h1>Diagnostico VesteIA</h1><p>Branco permite alteracao; vermelho mostra a area aplicada. Imagens somente na memoria. Atualize apos cada geracao.</p>' + content + '</html>').encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(page)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            try:
                self.wfile.write(page)
            except (BrokenPipeError, ConnectionResetError):
                pass
            return
        if self.path != '/health':
            return self.reply(404, {'detail': 'not found'})
        self.reply(200, {'ready': ENGINE is not None, 'provider': 'catvton'})

    def do_POST(self):
        if self.path != '/tryon':
            return self.reply(404, {'detail': 'not found'})
        # Only the backend talks to this loopback service, never a browser directly.
        if self.headers.get('Origin'):
            return self.reply(403, {'detail': 'browser requests disabled'})
        if not LOCK.acquire(blocking=False):
            return self.reply(429, {'detail': 'busy'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= MAX_BODY:
                return self.reply(413, {'detail': 'invalid body size'})
            data = json.loads(self.rfile.read(size))
            self.reply(200, infer(data))
        except (ValueError, KeyError, TypeError, OSError):
            self.reply(422, {'detail': 'invalid images'})
        except Exception as error:
            logging.exception('CatVTON generation failed')
            oom = ENGINE is not None and isinstance(error, ENGINE.torch.cuda.OutOfMemoryError)
            self.reply(503 if oom else 500, {'detail': 'GPU memory exhausted' if oom else 'generation failed'})
        finally:
            LOCK.release()
            if ENGINE is not None:
                ENGINE.torch.cuda.empty_cache()


if __name__ == '__main__':
    print('Carregando o CatVTON e os modelos já instalados...', flush=True)
    import app as ENGINE
    server = ThreadingHTTPServer(('127.0.0.1', 7861), Handler)
    print('VesteIA: CatVTON pronto em http://127.0.0.1:7861 (mantenha este terminal aberto).', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
