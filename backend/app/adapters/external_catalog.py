"""Mapeamento configurável de JSON externo; não acopla fabricante/grade ao domínio."""
from app.adapters.catalog_adapter import normalize_product

def read_path(value,path,default=None):
    for key in path.split('.'):
        if not isinstance(value,dict) or key not in value:return default
        value=value[key]
    return value

def adapt_external_product(payload,mapping):
    def fields(obj,spec):return {target:read_path(obj,path) for target,path in spec.items() if read_path(obj,path) is not None}
    product=fields(payload,mapping['product'])
    variants=[]
    for raw in read_path(payload,mapping.get('variants_path','variantes'),[]):
        variant=fields(raw,mapping['variant']);sizes=[]
        for row in read_path(raw,mapping.get('sizes_path','tamanhos'),[]):
            size=fields(row,mapping['size'])
            # A loja declara a unidade e o fator. Não há conversão ou reconhecimento implícito.
            size['medidas']={key:float(read_path(row,path))*mapping.get('measurement_factor',1) for key,path in mapping.get('measurements',{}).items() if read_path(row,path) is not None}
            sizes.append(size)
        variant['tamanhos']=sizes;variants.append(variant)
    product['variantes']=variants
    return normalize_product(product)
