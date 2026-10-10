"""Contratos de aparência e caimento sem banco ou inferência métrica por fotografia."""
import ast
from copy import deepcopy
from pathlib import Path
from typing import Literal
import math
import pytest
from pydantic import BaseModel, Field, field_validator, ValidationError
from app.services.comparacao_mvp import compare

source=ast.parse((Path(__file__).parents[1]/'app/api/mvp.py').read_text())
classes=[n for n in source.body if isinstance(n,ast.ClassDef) and n.name in ('Profile','CompareRequest')]
namespace={'BaseModel':BaseModel,'Field':Field,'field_validator':field_validator,'Literal':Literal,'math':math}
exec(compile(ast.Module(body=classes,type_ignores=[]),'mvp-contract','exec'),namespace)

@pytest.mark.parametrize('fit',['justo','slim','padrao','solto','largo','oversized'])
def test_fit_contract_and_unchanged_measurements(fit):
 profile=namespace['Profile'](estilo_cabelo='crespo',porte_corporal='largo',tom_pele='#855332')
 request=namespace['CompareRequest'](variant_id=1,perfil=profile,preferencia=fit)
 assert request.preferencia==fit
 product={'nome':'Camiseta','categoria':'camiseta'}
 variant={'modelagem':'regular','tamanhos':[{'id':1,'label':'M','medidas':{'largura_cm':52,'torax_cm':104},'legacy_product_id':1,'estoque':10}]}
 body=profile.model_dump();body['medidas']={'torax_cm':94}
 before=deepcopy((body,variant));result=compare(product,variant,body,fit)
 assert result['simulacao_fisica'] is False
 assert (body,variant)==before
 assert result['tamanhos'][0]['medidas']['largura_cm']==52

def test_invalid_hair_in_torso_rejected():
 with pytest.raises(ValidationError):namespace['Profile'](proporcao_tronco='crespo')
