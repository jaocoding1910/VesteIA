"""python scripts/import_catalog.py catalogo.json [--mapping mapeamento.json]"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.adapters.catalog_adapter import normalize_product
from app.adapters.external_catalog import adapt_external_product
from app.repositories.catalog_repository import import_product
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('catalog');parser.add_argument('--mapping');args=parser.parse_args()
    mapping=json.loads(Path(args.mapping).read_text(encoding='utf-8-sig')) if args.mapping else None
    data=json.loads(Path(args.catalog).read_text(encoding='utf-8-sig'))
    if not isinstance(data,list):raise ValueError('O catálogo deve ser uma lista de produtos')
    for item in data:
        product=adapt_external_product(item,mapping) if mapping else normalize_product(item)
        print('Importado produto',import_product(product))
