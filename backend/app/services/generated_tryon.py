"""Fronteira de geração visual: imagem sintetizada jamais entra no motor dimensional."""
from typing import Protocol

class VisualTryOnAdapter(Protocol):
    def generate(self,*,photo_path:str,garment_image:str)->dict: ...

class UnconfiguredVisualTryOn:
    def generate(self,*,photo_path:str,garment_image:str)->dict:
        return {'disponivel':False,'status':'servico_nao_configurado','renderer_alternativo':'2d',
                'mensagem':'Geração fotorrealista ainda não está configurada. Use a representação 2D.'}
