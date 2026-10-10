import base64, importlib.util, io, json
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import pytest
from PIL import Image
from app.services import tryon_service as service
spec=importlib.util.spec_from_file_location('worker',Path(__file__).resolve().parents[2]/'integracao/catvton/vesteia_worker.py')
worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
def photo(color='blue'):
 out=io.BytesIO();Image.new('RGB',(256,384),color).save(out,format='PNG');return out.getvalue()
@pytest.fixture
def local(monkeypatch):
 from contextlib import nullcontext
 captured={}
 def pipeline(**kwargs):captured.update(kwargs);return [Image.new('RGB',(384,512),'red')]
 def mask(image,category):
  captured['category']=category;m=Image.new('L',image.size,0);m.paste(255,(100,150,280,350));return {'mask':m}
 class Generator:
  def __init__(self,**kwargs):pass
  def manual_seed(self,value):return self
 monkeypatch.setattr(worker,'ENGINE',SimpleNamespace(args=SimpleNamespace(width=384,height=512),resize_and_padding=lambda im,size:im.resize(size),automasker=mask,mask_processor=SimpleNamespace(blur=lambda m,**kwargs:m),pipeline=pipeline,torch=SimpleNamespace(inference_mode=nullcontext,Generator=Generator,cuda=SimpleNamespace(empty_cache=lambda:None,OutOfMemoryError=MemoryError))))
 server=worker.ThreadingHTTPServer(('127.0.0.1',0),worker.Handler);thread=Thread(target=server.serve_forever,daemon=True);thread.start()
 monkeypatch.setenv('TRYON_PROVIDER','catvton');monkeypatch.setenv('TRYON_ENABLED','true');monkeypatch.setenv('TRYON_CATVTON_URL',f'http://127.0.0.1:{server.server_port}')
 yield captured,server
 server.shutdown();server.server_close();thread.join()
@pytest.mark.parametrize('category,expected',[('camiseta','upper'),('calca','lower'),('bermuda','lower'),('saia','lower'),('vestido','overall')])
def test_local_http_pipeline_contract(local,category,expected):
 captured,_=local;assert service.local_status(service.configuration())
 result=service.generate(photo(),photo('green'),category)
 assert result['provider']=='catvton';assert captured['category']==expected
 assert (captured['width'],captured['height'])==(384,512)
 im=Image.open(io.BytesIO(base64.b64decode(result['image'].split(',')[1])))
 assert im.size==(384,512);assert im.getpixel((10,10))[2]>200;assert im.getpixel((200,250))[0]>200

def test_local_busy_invalid_and_origin(local):
 _,server=local;url=f'http://127.0.0.1:{server.server_port}/tryon'
 def post(payload,headers=None):return urlopen(Request(url,data=json.dumps(payload).encode(),headers=headers or {},method='POST'))
 worker.LOCK.acquire()
 try:
  with pytest.raises(HTTPError) as err:post({})
  assert err.value.code==429
 finally:worker.LOCK.release()
 with pytest.raises(HTTPError) as err:post({'category':'upper','person':'bad','garment':'bad'})
 assert err.value.code==422
 with pytest.raises(HTTPError) as err:post({}, {'Origin':'http://example.test'})
 assert err.value.code==403
 assert service.local_status(service.configuration())
def test_local_configuration_and_offline(monkeypatch):
 monkeypatch.setenv('TRYON_ENABLED','true');monkeypatch.setenv('TRYON_PROVIDER','catvton');monkeypatch.setenv('TRYON_CATVTON_URL','https://external.invalid:7861')
 assert not service.configuration()['configured']
 monkeypatch.setenv('TRYON_CATVTON_URL','http://127.0.0.1:7861')
 monkeypatch.setattr(service,'urlopen',lambda *args,**kwargs:(_ for _ in ()).throw(OSError('offline')))
 assert not service.local_status(service.configuration())
 with pytest.raises(service.TryOnError,match='Sem resposta'):service.generate(photo(),photo())
