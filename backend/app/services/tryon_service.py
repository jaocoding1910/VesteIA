"""Google Virtual Try-On adapter. No local fake-generation fallback or disk photo storage."""
import base64
import io
import json
import os
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES=7*1024*1024
MAX_PIXELS=16_000_000
class TryOnError(Exception):
    def __init__(self,message,status=503):self.message=message;self.status=status;super().__init__(message)

def configuration():
    provider=os.getenv("TRYON_PROVIDER","google-vertex").strip()
    if provider=="catvton":
        url=os.getenv("TRYON_CATVTON_URL","http://127.0.0.1:7861").rstrip("/")
        valid=bool(re.fullmatch(r"http://(?:127\.0\.0\.1|localhost):[0-9]{2,5}",url))
        enabled=os.getenv("TRYON_ENABLED","false").lower()=="true"
        return {"provider":provider,"enabled":enabled,"configured":enabled and valid,"url":url,"model":"CatVTON"}

    project=os.getenv('TRYON_GOOGLE_PROJECT','').strip()
    region=os.getenv('TRYON_GOOGLE_REGION','us-central1').strip()
    model=os.getenv('TRYON_GOOGLE_MODEL','virtual-try-on-001').strip()
    valid=bool(re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]',project)) and bool(re.fullmatch(r'[a-z0-9-]+',region)) and bool(re.fullmatch(r'virtual-try-on-[a-z0-9-]+',model))
    enabled=os.getenv('TRYON_ENABLED','false').lower()=='true'
    return {'provider':'google-vertex','enabled':enabled,'configured':enabled and valid,'project':project,'region':region,'model':model}

def normalize_image(raw):
    if not raw or len(raw)>MAX_BYTES:raise TryOnError('Cada imagem deve ter até 7 MB.',413)
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.format not in {'PNG','JPEG','WEBP'}:raise TryOnError('Use uma imagem PNG, JPG ou WebP.',422)
            if im.width*im.height>MAX_PIXELS or min(im.size)<128:raise TryOnError('Use imagem com pelo menos 128 pixels por lado e até 16 megapixels.',422)
            image=ImageOps.exif_transpose(im).convert('RGBA')
            image.thumbnail((1536,1536))
            background=Image.new('RGB',image.size,'white');background.paste(image,mask=image.getchannel('A'))
            output=io.BytesIO();background.save(output,format='JPEG',quality=93)
            return base64.b64encode(output.getvalue()).decode('ascii')
    except (UnidentifiedImageError,OSError,Image.DecompressionBombError,Image.DecompressionBombWarning) as error:
        raise TryOnError('Não foi possível ler a imagem enviada.',422) from error

def access_token():
    token=os.getenv('TRYON_GOOGLE_ACCESS_TOKEN','').strip()
    if token:return token
    try:
        import google.auth
        from google.auth.transport.requests import Request as AuthRequest
        credentials,_=google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        credentials.refresh(AuthRequest())
        return credentials.token
    except Exception as error:
        raise TryOnError('Configure a autenticação Google Cloud no backend. Consulte ATIVAR_IA.md.') from error

def generate(person,garment,category="camiseta"):
    if configuration().get("provider")=="catvton":return generate_local(person,garment,category)
    config=configuration()
    if not config['configured']:raise TryOnError('A IA ainda não está configurada. Consulte ATIVAR_IA.md no backend.')
    endpoint=f"https://{config['region']}-aiplatform.googleapis.com/v1/projects/{config['project']}/locations/{config['region']}/publishers/google/models/{config['model']}:predict"
    payload={'instances':[{'personImage':{'image':{'bytesBase64Encoded':normalize_image(person)}},'productImages':[{'image':{'bytesBase64Encoded':normalize_image(garment)}}]}],'parameters':{'sampleCount':1}}
    request=Request(endpoint,data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {access_token()}','Content-Type':'application/json'},method='POST')
    try:
        with urlopen(request,timeout=120) as response:
            raw=response.read(12*1024*1024+1)
            if len(raw)>12*1024*1024:raise TryOnError('Resposta do serviço acima do limite.',502)
            result=json.loads(raw)
    except HTTPError as error:
        messages={401:'A autenticação Google expirou ou é inválida.',403:'Confira permissão Vertex AI, faturamento e API habilitada no Google Cloud.',429:'Limite do serviço atingido. Aguarde antes de tentar novamente.'}
        raise TryOnError(messages.get(error.code,'O Google não concluiu a geração. Confira modelo, região e disponibilidade do serviço.'),502) from error
    except (URLError,TimeoutError,OSError,ValueError) as error:
        raise TryOnError('A geração não foi concluída. Tente novamente mais tarde.',502) from error
    prediction=next((p for p in result.get('predictions',[]) if p.get('bytesBase64Encoded')),None)
    if not prediction:raise TryOnError('O serviço não retornou uma imagem. A entrada pode ter sido recusada; tente outra foto vestida.',422)
    try:generated=base64.b64decode(prediction['bytesBase64Encoded'],validate=True)
    except (ValueError,TypeError) as error:raise TryOnError('Resposta inválida do serviço.',502) from error
    # Validate output and strip metadata before returning a browser-safe image.
    return {'image':f'data:image/jpeg;base64,{normalize_image(generated)}','provider':'google-vertex','model':config['model']}


def local_status(config):
    if not config['configured']:return False
    try:
        with urlopen(config['url']+'/health',timeout=2) as response:
            data=json.loads(response.read(4096))
            return data.get('provider')=='catvton' and data.get('ready') is True
    except (URLError,OSError,ValueError):return False

def generate_local(person,garment,category):
    config=configuration()
    if not config['configured']:raise TryOnError('Ative o CatVTON local no .env do backend.')
    upper={'camiseta','camisa','blusa','regata','casaco','jaqueta'}
    lower={'calca','short','bermuda','saia'}
    cloth_type='upper' if category in upper else 'lower' if category in lower else 'overall' if category=='vestido' else None
    if not cloth_type:raise TryOnError('Categoria ainda não suportada pelo CatVTON.',422)
    payload={'person':normalize_image(person),'garment':normalize_image(garment),'category':cloth_type}
    request=Request(config['url']+'/tryon',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
    try:
        with urlopen(request,timeout=900) as response:
            raw=response.read(12*1024*1024+1)
            if len(raw)>12*1024*1024:raise TryOnError('Resposta local acima do limite.',502)
            result=json.loads(raw)
    except HTTPError as error:
        messages={429:'O CatVTON já está gerando uma imagem. Aguarde.',422:'O CatVTON não aceitou estas imagens. Tente outra foto vestida.',503:'Memória da GPU insuficiente. Feche o CatVTON antigo e outros programas que usam a GPU.'}
        raise TryOnError(messages.get(error.code,'O CatVTON não concluiu a geração. Confira o terminal da IA.'),error.code if error.code in messages else 502) from error
    except (URLError,OSError,ValueError) as error:
        raise TryOnError('Sem resposta do CatVTON local. Abra INICIAR_IA_LOCAL.bat e aguarde a mensagem de pronto.',503) from error
    try:generated=base64.b64decode(result['image'],validate=True)
    except (ValueError,KeyError,TypeError) as error:raise TryOnError('Resposta inválida do CatVTON.',502) from error
    return {'image':'data:image/jpeg;base64,'+normalize_image(generated),'provider':'catvton','model':'CatVTON'}
