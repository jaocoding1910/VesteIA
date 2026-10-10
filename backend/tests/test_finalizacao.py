from copy import deepcopy
import pytest
from app.adapters.catalog_adapter import normalize_product
from app.adapters.external_catalog import adapt_external_product
from app.services.avatar_photo_adapter import avatar_from_renderer
from app.services.comparacao_mvp import compare

def product():
 return {'external_product_id':'cliente-77','nome':'Peça estampada','categoria':'camiseta','variantes':[{'sku':'sku-azul','cor':'Azul','preco':12,'imagem_url':'/assets/produto.svg','metadata':{'visual':{'estampa_texto':'VSI','estampa_url':'/assets/vsi.svg'}},'tamanhos':[{'label':'1','medidas':{'torax_cm':102,'largura_cm':51}},{'label':'3XL','medidas':{'torax_cm':120,'largura_cm':60}}]}]}

def test_visual_metadata_sku_and_foreign_sizes_preserved():
 p=normalize_product(product());v=p['variantes'][0]
 assert v['sku']=='sku-azul';assert v['metadata']['visual']['estampa_texto']=='VSI'
 assert [s['label'] for s in v['tamanhos']]==['1','3XL']
 assert v['tamanhos'][1]['medidas']['largura_cm']==60

@pytest.mark.parametrize('value',[-1,0,float('inf'),float('nan'),1001])
def test_invalid_measurements_rejected(value):
 data=product();data['variantes'][0]['tamanhos'][0]['medidas']['largura_cm']=value
 with pytest.raises(ValueError):normalize_product(data)

def test_invalid_price_and_duplicate_sku_rejected():
 data=product();data['variantes'][0]['preco']=float('inf')
 with pytest.raises(ValueError):normalize_product(data)
 data=product();data['variantes'].append(deepcopy(data['variantes'][0]))
 with pytest.raises(ValueError):normalize_product(data)

def test_configurable_external_mapping_and_declared_units():
 source={'code':'fabricante-12','title':'Calça externa','type':'calca','options':[{'ref':'sku-12','color':'Preto','amount':99,'sizes':[{'number':'48','dimensions':{'waist':920,'length':1100}},{'number':'34','dimensions':{'waist':720,'length':980}}]}]}
 mapping={'product':{'external_product_id':'code','nome':'title','categoria':'type'},'variants_path':'options','variant':{'sku':'ref','cor':'color','preco':'amount'},'sizes_path':'sizes','size':{'label':'number'},'measurements':{'cintura_cm':'dimensions.waist','comprimento_cm':'dimensions.length'},'measurement_factor':.1}
 out=adapt_external_product(source,mapping)
 assert [s['label'] for s in out['variantes'][0]['tamanhos']]==['48','34']
 assert out['variantes'][0]['tamanhos'][0]['medidas']=={'cintura_cm':92,'comprimento_cm':110}

def test_oversized_changes_preference_not_body_or_catalog():
 p=product();v=p['variantes'][0]
 for i,s in enumerate(v['tamanhos']):s.update(id=i+1,legacy_product_id=i+1,estoque=10)
 profile={'medidas':{'torax_cm':94}};before=deepcopy(profile);measurements=deepcopy(v)
 regular=compare(p,v,profile,'padrao');large=compare(p,v,profile,'oversized')
 assert regular['recomendacao']['tamanho']=='1';assert large['recomendacao']['tamanho']=='3XL'
 assert profile==before and v==measurements

def test_photo_only_visual_configuration_never_infers_measurements():
 renderer={'pronto':True,'pontos':{}}
 for name,x,y in [('ombro_esquerdo',.36,.18),('ombro_direito',.64,.18),('quadril_esquerdo',.43,.49),('quadril_direito',.57,.49),('tornozelo_esquerdo',.44,.96),('tornozelo_direito',.56,.96)]:renderer['pontos'][name]={'x':x,'y':y}
 result=avatar_from_renderer(renderer)
 assert result['aplicavel'];assert result['usa_medida_fisica'] is False
 assert set(result['configuracao'])=={'porte_corporal','proporcao_tronco','proporcao_pernas'}
 assert avatar_from_renderer({})['aplicavel'] is False
 renderer['pontos']['tornozelo_direito']['y']=float('nan')
 assert avatar_from_renderer(renderer)['aplicavel'] is False
