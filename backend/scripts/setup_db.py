"""Inicialização aditiva. Execute da pasta backend: python scripts/setup_db.py [--seed]."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.database.database import conectar
from app.repositories.catalog_repository import import_product
from app.adapters.catalog_adapter import normalize_product
from app.repositories.legacy_bridge import bridge_legacy


def migrate():
    with conectar() as conn,conn.cursor() as cur:
        for file in sorted((Path(__file__).resolve().parents[1]/'migrations').glob('*.sql')):
            cur.execute(file.read_text())
            print('Migration:',file.name)
    print('SKUs legados ligados ao catálogo:',bridge_legacy())


def seed(include_extended=False):
    # Tabelas demonstrativas da loja de exemplo; não são medidas antropométricas inferidas.
    specs=[
      ('essential','Camiseta Oversized VesteIA Essential','camiseta',129.9,'oversized',['P','M','G','GG'],[48,52,56,60],[68,70,72,74],'100% algodão'),
      ('urban','Calça VesteIA Straight','calca',219.9,'regular',['34','36','38','40','42','44','46','48'],[36,38,40,42,44,46,48,50],[98,100,102,104,106,108,110,112],'Sarja de algodão'),
      ('weekend','Bermuda Weekend','short',119.9,'regular',['P','M','G','GG'],[36,39,42,45],[44,46,48,50],'Algodão e elastano'),
      ('flow','Saia Flow Midi','saia',159.9,'regular',['XS','S','M','L','XL'],[32,35,38,41,44],[70,72,74,76,78],'Viscose'),
      ('aurora','Vestido Aurora','vestido',249.9,'regular',['P','M','G','GG'],[44,48,52,56],[105,108,111,114],'Viscose e linho'),
      ('daily','Tênis Daily','calcado',289.9,'regular',['35','36','37','38','39','40','41','42'],[0]*8,[23,23.7,24.4,25.1,25.8,26.5,27.2,27.9],'Lona e borracha'),
      ('signature','Boné VesteIA Signature','bone',89.9,'regular',['Único'],[18],[12],'Algodão'),
    ]
    if not include_extended: specs=specs[:2]
    for slug,name,category,price,model,labels,widths,lengths,fabric in specs:
        variants=[]
        for color,hexcode in ([('Preto','#22252b'),('Off-white','#e5e1d7'),('Azul','#35576d'),('Violeta','#695682')] if category=='camiseta' else [('Preto','#262931'),('Areia','#bba98c')]):
            sizes=[]
            for n,label in enumerate(labels):
                measures={'comprimento_cm':lengths[n]}
                if category=='calcado': measures={'pe_cm':lengths[n],'comprimento_cm':lengths[n],'largura_cm':8.5+n*0.2}
                else:
                    measures['largura_cm']=widths[n]
                    if category in ('calca','short','saia'): measures.update(cintura_cm=widths[n]*2,quadril_cm=widths[n]*2+20,barra_cm=18+n*.8)
                    if category=='camiseta': measures.update(torax_cm=widths[n]*2,ombros_cm=44+n*2,manga_cm=21+n)
                    if category=='vestido': measures.update(torax_cm=widths[n]*2,cintura_cm=widths[n]*2-14,quadril_cm=widths[n]*2+8)
                sizes.append({'label':label,'estoque':12 if n!=len(labels)-1 else 4,'medidas':measures})
            variants.append({'sku':f'demo-{slug}-{color.lower()}','cor':color,'modelagem':model,'preco':price,
                'imagem_url':f'/assets/demo-{category}-{color.lower()}.svg' if category in ('camiseta','calca') else None,
                'metadata':{'cor_hex':hexcode,'tecido':fabric,'visual':{'estampa_texto':'VesteIA','estampa_cor':'#253344' if color in ('Off-white','Areia') else '#e6eef8','textura_url':False,'roupa_genero_urls':{g:f'/assets/roupa-real-{category}-{g}.svg' for g in ('masculino','feminino')} if category in ('camiseta','calca') else {},'encaixe_humano':{'feminino':{'subir_cintura_px':65},'masculino':{'subir_cintura_px':20}} if category=='calca' else {},'estampa_posicao':{'x':.5 if category=='camiseta' else .76,'y':.4 if category=='camiseta' else .14,'w':.47 if category=='camiseta' else .32,'h':.14 if category=='camiseta' else .08}}},'tamanhos':sizes})
        import_product(normalize_product({'external_product_id':f'demo-{slug}','nome':name,'categoria':category,
            'marca':'VesteIA','descricao':'Coleção demonstrativa Essential. Tabela de medidas da loja de exemplo.',
            'metadata':{'principal_mvp':category in ('camiseta','calca'),'demonstrativo':True,'publico':'feminino' if category in ('saia','vestido') else 'unissex'},'variantes':variants}))
    print('Seed idempotente: catálogo demonstrativo atualizado, registros anteriores preservados.')

if __name__=='__main__':
    migrate()
    if '--seed' in sys.argv or '--seed-all' in sys.argv: seed(include_extended='--seed-all' in sys.argv)
