from uuid import UUID
from typing import Literal
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field, field_validator
import math
from psycopg2.extras import Json
from app.database.database import conectar
from app.repositories.catalog_repository import list_products,find_product
from app.services.comparacao_mvp import compare

router=APIRouter(prefix='/mvp',tags=['Experiência comercial MVP'])

class Profile(BaseModel):
    apelido: str = Field(default='Você',min_length=1,max_length=60)
    estilo_avatar: Literal['humano','manequim']='humano'
    genero: Literal['masculino','feminino']='masculino'
    altura_aproximada_cm: float | None = Field(default=None,ge=100,le=230)
    peso_aproximado_kg: float | None = Field(default=None,ge=25,le=300)
    porte_corporal: Literal['estreito','medio','largo']='medio'
    proporcao_tronco: Literal['curto','media','longo']='media'
    proporcao_pernas: Literal['curtas','media','longas']='media'
    tom_pele: str = Field(default='#b87d57',pattern=r'^#[0-9a-fA-F]{6}$')
    cabelo: str = Field(default='#292018',pattern=r'^#[0-9a-fA-F]{6}$')
    estilo_cabelo: Literal['curto','longo','raspado','crespo']='curto'
    medidas: dict[str,float] = Field(default_factory=dict)
    @field_validator('medidas')
    @classmethod
    def check_measures(cls,value):
        bounds={'ombros_cm':(15,90),'torax_cm':(40,250),'cintura_cm':(30,250),'quadril_cm':(40,250),'pe_cm':(10,40)}
        for key,number in value.items():
            if key not in bounds or not math.isfinite(number) or not bounds[key][0]<=number<=bounds[key][1]:
                raise ValueError('Medida corporal inválida')
        return value

class CompareRequest(BaseModel):
    variant_id: int
    perfil: Profile
    preferencia: Literal['justo','slim','padrao','solto','largo','oversized']='padrao'

@router.get('/catalogo')
def catalog():
    return {'produtos':list_products(),'origem':'postgresql'}

@router.get('/produtos/{product_id}')
def product(product_id:int):
    found=find_product(product_id)
    if not found: raise HTTPException(404,'Produto não encontrado')
    return found

@router.post('/produtos/{product_id}/comparar')
def comparison(product_id:int,data:CompareRequest):
    found=product(product_id)
    variant=next((v for v in found['variantes'] if v['id']==data.variant_id),None)
    if not variant: raise HTTPException(404,'Variante não encontrada neste produto')
    if any(v<=0 or v>300 for v in data.perfil.medidas.values()): raise HTTPException(422,'Medidas corporais inválidas')
    return compare(found,variant,data.perfil.model_dump(),data.preferencia)

@router.put('/perfis/{profile_id}')
def save_profile(profile_id:UUID,data:Profile):
    if any(v<=0 or v>300 for v in data.medidas.values()): raise HTTPException(422,'Medidas corporais inválidas')
    with conectar() as conn,conn.cursor() as cur:
        cur.execute('''INSERT INTO client_profiles(id,apelido,perfil) VALUES (%s,%s,%s)
            ON CONFLICT(id) DO UPDATE SET apelido=EXCLUDED.apelido,perfil=EXCLUDED.perfil,updated_at=NOW()''',
            (str(profile_id),data.apelido,Json(data.model_dump())))
    return {'salvo':True}

@router.delete('/perfis/{profile_id}',status_code=204)
def delete_profile(profile_id:UUID):
    with conectar() as conn,conn.cursor() as cur:
        cur.execute('DELETE FROM client_profiles WHERE id=%s',(str(profile_id),))

class CartLine(BaseModel):
    size_id:int
    quantidade:int=Field(ge=1,le=99)

@router.post('/carrinho/validar')
def validate_cart(lines:list[CartLine]):
    available={s['id']:(p,v,s) for p in list_products() for v in p['variantes'] for s in v['tamanhos']}
    result=[]
    aggregated={}
    for line in lines:
        aggregated[line.size_id]=aggregated.get(line.size_id,0)+line.quantidade
    for size_id,quantity in aggregated.items():
        if quantity>99: raise HTTPException(409,'Quantidade agregada acima do limite')
        line=CartLine(size_id=size_id,quantidade=quantity)
        entry=available.get(line.size_id)
        if not entry: raise HTTPException(409,'Um item saiu do catálogo. Remova-o do carrinho.')
        p,v,s=entry
        if s['estoque'] is not None and s['estoque']<line.quantidade: raise HTTPException(409,f'Estoque insuficiente para {p["nome"]} ({s["label"]}).')
        result.append({'size_id':s['id'],'preco':v['preco'],'quantidade':line.quantidade,'nome':p['nome']})
    return {'itens':result,'total':round(sum(i['preco']*i['quantidade'] for i in result),2),'reserva_estoque':False,'checkout_disponivel':False}

@router.post('/avatar/foto/{session_id}')
def avatar_photo(session_id:int,authorization:str|None=Header(default=None)):
    from app.services.photo_privacy import authorize
    from app.api.provador import executar_pipeline_provador
    from app.services.avatar_photo_adapter import avatar_from_renderer
    from app.services.generated_tryon import UnconfiguredVisualTryOn
    token=authorization[7:] if authorization and authorization.startswith('Bearer ') else ''
    if not authorize(session_id,token): raise HTTPException(403,'Captura privada ou expirada')
    data=executar_pipeline_provador(session_id,preferencia_caimento='padrao')
    result=avatar_from_renderer(data.get('renderer_avatar_2d') or {})
    result['geracao_fotorrealista']=UnconfiguredVisualTryOn().generate(photo_path='',garment_image='')
    return result
