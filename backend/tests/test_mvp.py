"""Contrato/comparação e integração real com banco isolado configurado em .env."""
from copy import deepcopy
from io import BytesIO
from uuid import uuid4
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import conectar
from app.services.comparacao_mvp import compare
from app.adapters.catalog_adapter import normalize_product
from app.repositories.catalog_repository import list_products
from app.services.photo_privacy import purge_expired
from scripts.setup_db import migrate,seed

@pytest.fixture(scope='module')
def client():
    import os
    assert os.getenv('DB_NAME','').endswith('_test'), 'Configure um banco isolado cujo nome termine em _test'
    migrate();seed(include_extended=True)
    return TestClient(app)

@pytest.fixture
def tee():
    return next(p for p in list_products() if p['external_product_id']=='demo-essential')

def test_seed_is_idempotent(client):
    with conectar() as conn,conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM produtos');before=cur.fetchone()[0]
    seed()
    with conectar() as conn,conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM produtos');assert cur.fetchone()[0]==before
    assert len(client.get('/mvp/catalogo').json()['produtos'])>=6
    assert sum(bool(p['metadata'].get('principal_mvp')) for p in list_products())==2

def test_dynamic_catalog_order(client):
    products=client.get('/mvp/catalogo').json()['produtos']
    pants=next(p for p in products if p['categoria']=='calca')
    assert [s['label'] for s in pants['variantes'][0]['tamanhos']]==['34','36','38','40','42','44','46','48']
    assert all(s['legacy_product_id'] for p in products for v in p['variantes'] for s in v['tamanhos'])

def test_actual_measurements_and_appearance_invariance(tee):
    profile={'medidas':{'torax_cm':94,'ombros_cm':44},'genero':'masculino','tom_pele':'#000','cabelo':'#000'}
    first=compare(tee,tee['variantes'][0],profile)
    changed=compare(tee,tee['variantes'][0],{**profile,'genero':'feminino','tom_pele':'#fff','cabelo':'#fff'})
    assert first['recomendacao']==changed['recomendacao']
    assert first['recomendacao']['origem']=='medidas_informadas'
    assert first['recomendacao']['tamanho']=='M'
    assert len({tuple(i['motivos']) for i in first['tamanhos']})==4

def test_missing_measurements_do_not_invent_fit(tee):
    response=compare(tee,tee['variantes'][0],{'medidas':{}})
    assert response['recomendacao'] is None
    assert all(i['caimento']=='Sem medidas suficientes' for i in response['tamanhos'])
    assert all(i['eixos_comparados']==0 for i in response['tamanhos'])

def test_partial_and_low_confidence(tee):
    assert compare(tee,tee['variantes'][0],{'medidas':{'torax_cm':94}})['recomendacao']['confianca']=='Limitada'
    assert compare(tee,tee['variantes'][0],{'medidas':{},'altura_aproximada_cm':175,'peso_aproximado_kg':70})['recomendacao']['confianca']=='Baixa'

def test_stock_excluded_from_recommendation(tee):
    item=deepcopy(tee);variant=item['variantes'][0]
    for size in variant['tamanhos']:size['estoque']=0
    assert compare(item,variant,{'medidas':{'torax_cm':94}})['recomendacao'] is None

def test_adapter_preserves_foreign_order_and_rejects_duplicates():
    payload={'external_product_id':'test-contract','nome':'Test','categoria':'camiseta','variantes':[{'sku':'test','cor':'Preto','preco':10,'tamanhos':[{'label':'2XL'},{'label':'XS'}]}]}
    assert [s['label'] for s in normalize_product(payload)['variantes'][0]['tamanhos']]==['2XL','XS']
    payload['variantes'][0]['tamanhos'].append({'label':'XS'})
    with pytest.raises(ValueError):normalize_product(payload)

def test_profile_comparison_and_validation(client,tee):
    uid=uuid4();profile={'apelido':'Teste','genero':'feminino','medidas':{'torax_cm':96}}
    assert client.put(f'/mvp/perfis/{uid}',json=profile).status_code==200
    assert client.post(f'/mvp/produtos/{tee["id"]}/comparar',json={'variant_id':tee['variantes'][0]['id'],'perfil':profile}).status_code==200
    assert client.post(f'/mvp/produtos/{tee["id"]}/comparar',json={'variant_id':999999,'perfil':profile}).status_code==404
    assert client.put(f'/mvp/perfis/{uid}',json={**profile,'medidas':{'torax_cm':-2}}).status_code==422
    assert client.delete(f'/mvp/perfis/{uid}').status_code==204

def test_cart_uses_current_prices_and_stock(client,tee):
    size=tee['variantes'][0]['tamanhos'][0]
    good=client.post('/mvp/carrinho/validar',json=[{'size_id':size['id'],'quantidade':2}])
    assert good.status_code==200
    assert good.json()['total']==pytest.approx(tee['variantes'][0]['preco']*2)
    assert client.post('/mvp/carrinho/validar',json=[{'size_id':size['id'],'quantidade':99}]).status_code==409
    assert client.post('/mvp/carrinho/validar',json=[{'size_id':999999,'quantidade':1}]).status_code==409
    assert client.post('/mvp/carrinho/validar',json=[{'size_id':size['id'],'quantidade':7},{'size_id':size['id'],'quantidade':7}]).status_code==409

def test_photo_validation_and_private_lifecycle(client,tee):
    legacy=tee['variantes'][0]['tamanhos'][0]['legacy_product_id'];data={'produto_id':legacy,'modo':'foto'}
    assert client.post('/provador/preparar',data=data,files={'foto':('bad.png',b'not-image','image/png')}).status_code==400
    assert client.post('/provador/preparar',data=data,files={'foto':('bad.gif',b'GIF','image/gif')}).status_code==400
    image=BytesIO();Image.new('RGB',(240,320),'white').save(image,format='PNG')
    capture=client.post('/provador/preparar',data=data,files={'foto':('valid.png',image.getvalue(),'image/png')})
    assert capture.status_code==200,capture.text
    created=capture.json();session=created['sessao_id'];headers={'Authorization':'Bearer '+created['access_token']}
    assert client.get(f'/provador/sessoes/{session}').status_code==403
    assert client.get(f'/provador/sessoes/{session}',headers=headers).status_code==200
    result=client.post(f'/provador/sessoes/{session}/executar',headers=headers)
    assert result.status_code==200,result.text
    assert result.json()['deteccao_humana']['pessoa_detectada'] is False
    assert client.delete(f'/provador/sessoes/{session}',headers=headers).status_code==204
    assert client.get(f'/provador/sessoes/{session}',headers=headers).status_code==403
    assert client.get('/provador/sessoes').status_code==403

def test_legacy_contracts_preserved(client,tee):
    old=tee['variantes'][0]['tamanhos'][0]['legacy_product_id']
    assert client.get('/produtos').status_code==200
    assert client.get(f'/produtos/{old}').status_code==200
    assert client.get(f'/produtos/{old}/grade-tamanhos').status_code==200
    result=client.post('/avatar/vestibilidade',json={'produto_id':old,'genero':'masculino','altura_aproximada_cm':175,'peso_aproximado_kg':70})
    assert result.status_code==200,result.text
    assert result.json()['vestibilidade_calculada'] is True

@pytest.mark.parametrize('category',['camiseta','calca','short','saia','vestido','calcado'])
def test_photo_detected_person_six_category_pipeline(client,category):
    from pathlib import Path
    asset=Path(__file__).resolve().parents[2]/'frontend/public/assets/avatar-masculino-natural.png'
    product=next(p for p in list_products() if p['categoria']==category)
    legacy=product['variantes'][0]['tamanhos'][0]['legacy_product_id']
    capture=client.post('/provador/preparar',data={'produto_id':legacy,'modo':'foto'},files={'foto':('model.png',asset.read_bytes(),'image/png')})
    assert capture.status_code==200,capture.text
    data=capture.json();session=data['sessao_id'];headers={'Authorization':'Bearer '+data['access_token']}
    try:
        result=client.post(f'/provador/sessoes/{session}/executar',headers=headers)
        assert result.status_code==200,result.text
        response=result.json()
        assert response['deteccao_humana']['pessoa_detectada'] is True
        assert response['renderer_avatar_2d']['pronto'] is True
        assert response['vestimenta_avatar_2d']['vestida_no_avatar'] is True
        if category=='camiseta':
            assert client.post(f'/mvp/avatar/foto/{session}').status_code==403
            avatar=client.post(f'/mvp/avatar/foto/{session}',headers=headers)
            assert avatar.status_code==200,avatar.text
            assert avatar.json()['aplicavel'] is True
            assert avatar.json()['usa_medida_fisica'] is False
            assert avatar.json()['geracao_fotorrealista']['disponivel'] is False
        # Sem altura de referência fornecida, não existe escala métrica absoluta.
        assert response['deteccao_humana'].get('escala_corporal',{}).get('conversao_disponivel') is not True
    finally:
        client.delete(f'/provador/sessoes/{session}',headers=headers)

def test_expired_capture_files_deleted(client,tee):
    from pathlib import Path
    image=BytesIO();Image.new('RGB',(120,160),'white').save(image,format='PNG')
    legacy=tee['variantes'][0]['tamanhos'][0]['legacy_product_id']
    capture=client.post('/provador/preparar',data={'produto_id':legacy},files={'foto':('expiring.png',image.getvalue(),'image/png')}).json()
    with conectar() as conn,conn.cursor() as cur:
        cur.execute("UPDATE sessoes_provador SET expires_at=NOW()-INTERVAL '1 hour' WHERE id=%s RETURNING caminho_arquivo",(capture['sessao_id'],))
        file=Path(__file__).resolve().parents[1]/cur.fetchone()[0]
    assert file.exists()
    assert purge_expired()>=1
    assert not file.exists()

def test_too_small_catalog_does_not_recommend(tee):
    assert compare(tee,tee['variantes'][0],{'medidas':{'torax_cm':200,'ombros_cm':70}})['recomendacao'] is None
