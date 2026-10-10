import base64
import importlib.util
import io
import json
from pathlib import Path
import pytest
from PIL import Image
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.services import selfie_avatar as service
from app.api import selfie_api as api
from app.services.tryon_service import TryOnError

def photo():
    output=io.BytesIO();Image.new('RGB',(256,256),'gray').save(output,format='PNG');return output.getvalue()

class Response:
    def __init__(self,value): self.value=value
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,limit):return json.dumps(self.value).encode()

def test_avatar_contract(monkeypatch):
    calls=[]
    def send(request,timeout):
        calls.append(json.loads(request.data))
        return Response({'image':base64.b64encode(photo()).decode()})
    monkeypatch.setattr(service,'urlopen',send)
    answer=service.generate_avatar(photo(),'masculino')
    assert answer['image'].startswith('data:image/jpeg;base64,')
    assert answer['body_source']=='template' and answer['experimental']
    assert calls[0]['template']=='masculino'
    assert base64.b64decode(calls[0]['selfie']).startswith(b'\xff\xd8')

def test_invalid_selfie_never_reaches_worker(monkeypatch):
    monkeypatch.setattr(service,'urlopen',lambda *a,**k:pytest.fail('Must not send'))
    with pytest.raises(TryOnError):service.generate_avatar(b'bad','masculino')

def test_invalid_worker_image(monkeypatch):
    monkeypatch.setattr(service,'urlopen',lambda *a,**k:Response({'image':'bad'}))
    with pytest.raises(TryOnError):service.generate_avatar(photo(),'masculino')

def test_consent_enum_and_busy(monkeypatch):
    app=FastAPI();app.include_router(api.router);client=TestClient(app)
    calls=[]
    monkeypatch.setattr(api,'generate_avatar',lambda *a:calls.append(a) or {'image':'test'})
    def send(consent='true',template='masculino'):
        return client.post('/mvp/ia/avatar',data={'consent':consent,'template':template},files={'selfie':('p.png',photo(),'image/png')})
    assert send('false').status_code==422
    assert send(template='../bad').status_code==422
    assert not calls
    api.slots.acquire()
    try:assert send().status_code==429
    finally:api.slots.release()
    assert send().status_code==200 and len(calls)==1

def test_photo_expansion_preserves_visible_region():
    path=Path(__file__).resolve().parents[2]/'integracao/avatar/engine.py'
    spec=importlib.util.spec_from_file_location('avatar_engine_test',path)
    engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    source=Image.new('RGB',(400,600),'blue')
    canvas,mask,reference=engine.prepare_photo(source,(140,110,90,90))
    assert canvas.size==mask.size==(512,768)
    assert mask.getextrema()==(0,255)
    assert mask.getpixel((256,750))==255
    assert reference.width>0
    result=Image.composite(Image.new('RGB',canvas.size,'red'),canvas,mask)
    assert result.getpixel((256,130))==canvas.getpixel((256,130))


def test_expanded_avatar_metadata(monkeypatch):
    monkeypatch.setattr(service,'urlopen',lambda *a,**k:Response({'image':base64.b64encode(photo()).decode(),'body_source':'photo_outpaint'}))
    answer=service.generate_avatar(photo(),'masculino')
    assert answer['body_source']=='photo_outpaint'
    assert 'estimados' in answer['message']
