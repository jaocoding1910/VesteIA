from threading import BoundedSemaphore
from fastapi import APIRouter,File,Form,HTTPException,UploadFile
from app.services.tryon_service import configuration,generate,TryOnError,MAX_BYTES,local_status
from app.repositories.catalog_repository import find_product
router=APIRouter(prefix='/mvp/ia',tags=['Prévia realista IA'])
slots=BoundedSemaphore(1)
CATEGORIES={'camiseta','camisa','blusa','regata','casaco','jaqueta','calca','short','bermuda','saia','vestido'}
@router.get('/status')
def status():
    config=configuration()
    ready=config['configured'] and (local_status(config) if config.get('provider')=='catvton' else True)
    return {'configured':ready,'provider':config.get('provider','google-vertex'),'categories':sorted(CATEGORIES),'message':'Pronto para solicitar uma prévia.' if ready else 'Abra INICIAR_IA_LOCAL.bat e aguarde o CatVTON ficar pronto.' if config.get('provider')=='catvton' else 'IA não configurada. Siga ATIVAR_IA.md no backend.'}
@router.post('/previa')
def preview(product_id:int=Form(...),variant_id:int=Form(...),consent:bool=Form(...),person:UploadFile=File(...),garment:UploadFile=File(...)):
    try:
        if not consent:raise HTTPException(422,'Autorize o envio das imagens para gerar a prévia.')
        if not configuration()['configured']:raise HTTPException(503,'IA não configurada. Siga ATIVAR_IA.md no backend.')
        product=find_product(product_id)
        if not product or not any(v['id']==variant_id for v in product['variantes']):raise HTTPException(404,'Produto ou variante não encontrado.')
        if product['categoria'] not in CATEGORIES:raise HTTPException(422,'Esta categoria ainda não está habilitada na prévia com IA.')
        if not slots.acquire(blocking=False):raise HTTPException(429,'Há uma geração em andamento. Aguarde e tente novamente.')
        try:
            person_bytes=person.file.read(MAX_BYTES+1);garment_bytes=garment.file.read(MAX_BYTES+1)
            return generate(person_bytes,garment_bytes,product['categoria'])
        except TryOnError as error:raise HTTPException(error.status,error.message) from error
        finally:slots.release()
    finally:
        person.file.close();garment.file.close()
