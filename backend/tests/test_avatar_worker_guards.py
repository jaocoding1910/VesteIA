import importlib.util
from pathlib import Path
import io
import json

def worker():
    path=Path(__file__).resolve().parents[2]/'integracao/avatar/server.py'
    spec=importlib.util.spec_from_file_location('avatar_worker_test',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def handler(module,headers=None,payload=b'{}'):
    instance=object.__new__(module.Handler);instance.path='/avatar';instance.headers=headers or {'Content-Length':str(len(payload))};instance.rfile=io.BytesIO(payload)
    calls=[];instance.reply=lambda status,value:calls.append((status,value));return instance,calls

def test_worker_rejects_browser(monkeypatch):
    module=worker();instance,calls=handler(module,{'Origin':'http://localhost:5173'})
    monkeypatch.setattr(module.subprocess,'run',lambda *a,**k:(_ for _ in ()).throw(AssertionError('Do not launch')))
    instance.do_POST();assert calls[0][0]==403

def test_catvton_running_blocks_avatar_and_releases_slot(monkeypatch):
    module=worker();instance,calls=handler(module)
    monkeypatch.setattr(module.Path,'exists',lambda self:True)
    monkeypatch.setattr(module,'cat_running',lambda:True)
    instance.do_POST();assert calls[0][0]==409
    assert module.LOCK.acquire(False);module.LOCK.release()

def test_engine_payload_uses_pipe_not_disk(monkeypatch):
    module=worker();instance,calls=handler(module,payload=b'{"selfie":"test","template":"masculino"}')
    monkeypatch.setattr(module.Path,'exists',lambda self:True)
    monkeypatch.setattr(module,'cat_running',lambda:False)
    def run(argv,**kwargs):
        assert 'selfie' in json.loads(kwargs['input'])
        assert 'shell' not in kwargs
        assert argv==[module.sys.executable,str(module.ROOT/'engine.py')]
        return type('Process',(),{'stdout':'{"image":"test"}','returncode':0})()
    monkeypatch.setattr(module.subprocess,'run',run)
    instance.do_POST();assert calls==[(200,{'image':'test'})]
