"""Contrato neutro de importação para conectores de e-commerce futuros."""
import math
from pydantic import BaseModel, Field, field_validator
from app.services.categorias_vestuario import normalizar_categoria

class SizeInput(BaseModel):
    label: str = Field(min_length=1,max_length=30)
    sort_order: int | None = None
    estoque: int | None = Field(default=None,ge=0)
    medidas: dict[str,float] = Field(default_factory=dict)
    @field_validator('medidas')
    @classmethod
    def valid_measures(cls,value):
        if any(not math.isfinite(v) or v<=0 or v>1000 for v in value.values()):
            raise ValueError('Medidas da peça devem ser positivas e inferiores a 1000 cm')
        return value

class VariantInput(BaseModel):
    sku: str = Field(min_length=1,max_length=120)
    cor: str = Field(min_length=1,max_length=100)
    modelagem: str = 'regular'
    preco: float = Field(ge=0,allow_inf_nan=False)
    imagem_url: str | None = None
    metadata: dict = Field(default_factory=dict)
    tamanhos: list[SizeInput] = Field(min_length=1)
    @field_validator('tamanhos')
    @classmethod
    def unique_sizes(cls,sizes):
        if len({s.label for s in sizes})!=len(sizes): raise ValueError('Tamanhos duplicados')
        return sizes

class ProductInput(BaseModel):
    external_product_id: str = Field(min_length=1,max_length=255)
    nome: str = Field(min_length=1,max_length=255)
    categoria: str
    marca: str | None = None
    descricao: str | None = None
    metadata: dict = Field(default_factory=dict)
    variantes: list[VariantInput] = Field(min_length=1)
    @field_validator('categoria')
    @classmethod
    def category(cls,value):
        category='bone' if value.strip().lower() in ('boné','bone','cap') else normalizar_categoria(value)
        if not category: raise ValueError('Categoria não reconhecida')
        return category
    @field_validator('variantes')
    @classmethod
    def unique_skus(cls,variants):
        if len({v.sku for v in variants})!=len(variants): raise ValueError('SKUs duplicados')
        return variants


def normalize_product(payload):
    product=ProductInput.model_validate(payload).model_dump()
    for variant in product['variantes']:
        for order,size in enumerate(variant['tamanhos']):
            if size['sort_order'] is None: size['sort_order']=order
    return product
