import base64,io,json
import pytest
from PIL import Image
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.services import tryon_service as service
from app.api import tryon_api as api

def photo():
 out=io.BytesIO();Image.new('RGB',(256,384),'navy').save(out,format='PNG');return out.getvalue()

def test_image_limits():
 assert base64.b64decode(service.normalize_image(photo())).startswith(b'\xff\xd8')
 for raw in [b'bad',b'x'*(service.MAX_BYTES+1)]:
  with pytest.raises(service.TryOnError):service.normalize_image(raw)

def test_disabled_provider(monkeypatch):
 monkeypatch.setenv('TRYON_ENABLED','false')
 monkeypatch.setattr(service,'urlopen',lambda *a,**k:pytest.fail('Unexpected call'))
 with pytest.raises(service.TryOnError):service.generate(photo(),photo())

def test_google_contract(monkeypatch):
 monkeypatch.setenv('TRYON_ENABLED','true');monkeypatch.setenv('TRYON_GOOGLE_PROJECT','vesteia-test');monkeypatch.setenv('TRYON_GOOGLE_ACCESS_TOKEN','unit-test-token')
 captured={}
 class Response:
  def __enter__(self):return self
  def __exit__(self,*a):pass
  def read(self,n):return json.dumps({'predictions':[{'mimeType':'image/png','bytesBase64Encoded':base64.b64encode(photo()).decode()}]}).encode()
 def send(request,timeout):captured['data']=json.loads(request.data);captured['url']=request.full_url;return Response()
 monkeypatch.setattr(service,'urlopen',send)
 assert service.generate(photo(),photo())['image'].startswith('data:image/jpeg;base64,')
 assert captured['data']['parameters']=={'sampleCount':1}
 assert 'personImage' in captured['data']['instances'][0]
 assert len(captured['data']['instances'][0]['productImages'])==1
 assert 'virtual-try-on-001:predict' in captured['url']

def test_route_guards(monkeypatch):
 monkeypatch.setattr(api,'configuration',lambda:{'configured':True})
 monkeypatch.setattr(api,'find_product',lambda id:{'categoria':'camiseta','variantes':[{'id':2}]})
 calls=[];monkeypatch.setattr(api,'generate',lambda p,g,c:calls.append((p,g,c)) or {'image':'test'})
 app=FastAPI();app.include_router(api.router);client=TestClient(app)
 def send(consent='true',variant='2'):
  return client.post('/mvp/ia/previa',data={'product_id':'1','variant_id':variant,'consent':consent},files={'person':('p.png',photo(),'image/png'),'garment':('g.png',photo(),'image/png')})
 assert send('false').status_code==422;assert send(variant='99').status_code==404;assert not calls
 api.slots.acquire()
 try:assert send().status_code==429
 finally:api.slots.release()
 assert send().status_code==200;assert len(calls)==1

def test_upload_middleware(monkeypatch):
 import ast
 from pathlib import Path
 from starlette.responses import JSONResponse
 tree=ast.parse((Path(__file__).resolve().parents[1]/'app/main.py').read_text())
 node=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='limit_ai_upload');node.decorator_list=[]
 namespace={'JSONResponse':JSONResponse,'origens_permitidas':['http://localhost:5173']}
 exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'limits','exec'),namespace)
 app=FastAPI();app.middleware('http')(namespace['limit_ai_upload'])
 @app.post('/mvp/ia/previa')
 def endpoint():return {'ok':True}
 client=TestClient(app)
 assert client.post('/mvp/ia/previa',content='x',headers={'origin':'https://other.example'}).status_code==403
 assert client.post('/mvp/ia/previa',content='x',headers={'content-length':str(16*1024*1024)}).status_code==413
 assert client.post('/mvp/ia/previa',content='x',headers={'origin':'http://localhost:5173'}).status_code==200
