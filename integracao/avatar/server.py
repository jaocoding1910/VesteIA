"""Servidor local sem fotos em disco; engine isolado para liberar a GPU."""
import json
import subprocess
import sys
from pathlib import Path
from threading import BoundedSemaphore
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import URLError

ROOT=Path(__file__).resolve().parent
LOCK=BoundedSemaphore(1)
MAX_BODY=10*1024*1024

def cat_running():
    try:
        with urlopen("http://127.0.0.1:7861/health",timeout=1) as response:
            return json.loads(response.read(4096)).get("ready") is True
    except (URLError,OSError,ValueError): return False

class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup();self.connection.settimeout(30)
    def reply(self,status,value):
        payload=json.dumps(value).encode();self.send_response(status)
        self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(payload)));self.end_headers()
        try:self.wfile.write(payload)
        except (BrokenPipeError,ConnectionResetError):pass
    def do_GET(self):
        if self.path!="/health":return self.reply(404,{"detail":"not found"})
        self.reply(200,{"provider":"ip-adapter-face-local","models_ready":(ROOT/"models-ready.txt").exists()})
    def do_POST(self):
        if self.path!="/avatar":return self.reply(404,{"detail":"not found"})
        if self.headers.get("Origin"):return self.reply(403,{"detail":"browser requests disabled"})
        if not LOCK.acquire(blocking=False):return self.reply(429,{"detail":"Já existe um avatar sendo gerado."})
        try:
            if not (ROOT/"models-ready.txt").exists():return self.reply(503,{"detail":"Execute CONFIGURAR_AVATAR_LOCAL.bat antes de gerar o avatar."})
            if cat_running():return self.reply(409,{"detail":"Pause somente a IA CatVTON com Ctrl+C antes de gerar o avatar. Isso libera a GPU. Depois de aprovar o avatar, inicie a IA CatVTON novamente para vestir a peça."})
            size=int(self.headers.get("Content-Length","0"))
            if not 0<size<=MAX_BODY:return self.reply(413,{"detail":"Imagem acima do limite."})
            payload=json.loads(self.rfile.read(size))
            if not isinstance(payload,dict):raise ValueError()
            process=subprocess.run([sys.executable,str(ROOT/"engine.py")],input=json.dumps(payload),text=True,encoding="utf-8",stdout=subprocess.PIPE,timeout=1100)
            try:result=json.loads(process.stdout)
            except ValueError:return self.reply(503,{"detail":"Gerador falhou. Confira o terminal do avatar."})
            self.reply(200 if process.returncode==0 else 422,result)
        except subprocess.TimeoutExpired:self.reply(503,{"detail":"O avatar excedeu o tempo limite. Confira a memória disponível."})
        except (OSError,ValueError,TypeError):self.reply(422,{"detail":"Entrada inválida."})
        finally:LOCK.release()

if __name__=="__main__":
    server=ThreadingHTTPServer(("127.0.0.1",7862),Handler)
    print("Avatar experimental pronto em http://127.0.0.1:7862. Modelos carregam somente ao gerar.",flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
