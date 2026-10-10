"""Cria banco demonstrativo separado e importa a loja FORMA. Nunca apaga dados."""
import argparse
import os
import re
import shutil
import sys
from pathlib import Path
import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv,set_key
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def allowed_database(name):
    return bool(re.fullmatch(r'vesteia_loja_[a-z0-9_]*(demo|test)',name))

def create_database(name):
    if not allowed_database(name):raise ValueError('Use um banco separado: vesteia_loja_demo ou vesteia_loja_test.')
    connection=psycopg2.connect(host=os.getenv('DB_HOST','localhost'),port=os.getenv('DB_PORT','5432'),user=os.getenv('DB_USER'),password=os.getenv('DB_PASSWORD'),dbname='postgres',connect_timeout=5)
    try:
        connection.autocommit=True
        with connection.cursor() as cur:
            cur.execute('SELECT 1 FROM pg_database WHERE datname=%s',(name,))
            if not cur.fetchone():
                cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
                print('Banco separado criado:',name)
            else:print('Banco demonstrativo existente:',name)
    finally:connection.close()

def setup(name):
    create_database(name)
    os.environ['DB_NAME']=name
    from app.database.database import conectar
    # Recusa um banco que já contenha outro catálogo; nenhuma limpeza é feita.
    with conectar() as conn,conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.catalog_products')")
        if cur.fetchone()[0]:
            cur.execute("SELECT COUNT(*) FROM catalog_products WHERE metadata->>'loja_demo' IS DISTINCT FROM 'forma'")
            if cur.fetchone()[0]:raise ValueError('O banco contém outro catálogo. Escolha outro nome de banco demo/test; nada foi removido.')
    from scripts.setup_db import migrate
    from app.adapters.catalog_adapter import normalize_product
    from app.repositories.catalog_repository import import_product
    migrate()
    catalog=json.loads((ROOT.parent/'docs/catalogo-loja-forma.json').read_text(encoding='utf-8'))
    for product in catalog['produtos']:
        import_product(normalize_product(product))
        print('Importado:',product['nome'])
    source=ROOT/'.env';target=ROOT/'.env.loja-demo'
    if source.exists():shutil.copyfile(source,target)
    else:shutil.copyfile(ROOT/'.env.example',target)
    set_key(str(target),'DB_NAME',name)
    print('Pronto. Configuração preparada em backend/.env.loja-demo; o .env atual foi preservado.')
    print('Para usar a loja: faça uma cópia do .env atual, copie .env.loja-demo para .env e reinicie o backend.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--database',default='vesteia_loja_demo');args=parser.parse_args()
    load_dotenv(ROOT/'.env')
    try:setup(args.database)
    except (psycopg2.Error,ValueError) as error:
        print('Não foi possível preparar a loja:',str(error).splitlines()[0],file=sys.stderr)
        print('Confira PostgreSQL, .env e permissão CREATE DATABASE. O catálogo anterior não foi apagado.',file=sys.stderr)
        sys.exit(1)
