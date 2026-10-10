import json
from pathlib import Path
from scripts.setup_loja_demo import allowed_database
from app.adapters.catalog_adapter import normalize_product

def test_database_names_are_isolated():
    assert allowed_database('vesteia_loja_demo')
    assert allowed_database('vesteia_loja_2_test')
    for name in ['postgres','vesteia','vesteia_loja_producao','vesteia_loja_demo;DROP DATABASE x']:
        assert not allowed_database(name)

def test_four_demo_products_and_measures():
    catalog=json.loads((Path(__file__).resolve().parents[2]/'docs/catalogo-loja-forma.json').read_text())
    products=[normalize_product(p) for p in catalog['produtos']]
    assert {p['categoria'] for p in products}=={'camiseta','calca','short','vestido'}
    assert len({p['external_product_id'] for p in products})==4
    for p in products:
        assert p['metadata']['loja_demo']=='forma'
        sizes=p['variantes'][0]['tamanhos']
        assert [s['label'] for s in sizes]==['P','M','G','GG']
        assert sizes[-1]['medidas']['largura_cm']>sizes[0]['medidas']['largura_cm']
