"""Expõe os registros anteriores na nova loja sem copiar, apagar ou renumerar SKUs."""
from hashlib import sha256
from psycopg2.extras import RealDictCursor,Json
from app.database.database import conectar
from app.services.categorias_vestuario import normalizar_categoria

def bridge_legacy():
    count=0
    with conectar() as conn,conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT p.* FROM produtos p LEFT JOIN catalog_sizes s ON s.legacy_product_id=p.id WHERE s.id IS NULL ORDER BY p.id')
        rows=cur.fetchall()
        for row in rows:
            category=normalizar_categoria(row['categoria']) or row['categoria']
            identity=sha256((row['nome'].strip().lower()+'|'+category).encode()).hexdigest()[:20]
            external='legacy-'+identity
            cur.execute('''INSERT INTO catalog_products(external_product_id,nome,categoria,marca,metadata)
                VALUES (%s,%s,%s,%s,%s) ON CONFLICT(external_product_id) WHERE external_product_id IS NOT NULL
                DO UPDATE SET external_product_id=EXCLUDED.external_product_id RETURNING id''',
                (external,row['nome'],category,None,Json({'origem':'catalogo_legado','publico':'unissex'})))
            product_id=cur.fetchone()['id']
            variant_key=sha256((row['cor']+'|'+str(row['modelagem'])).encode()).hexdigest()[:12]
            sku=external+'-'+variant_key
            cur.execute('''INSERT INTO catalog_variants(product_id,sku,cor,modelagem,preco) VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT(sku) WHERE sku IS NOT NULL DO UPDATE SET sku=EXCLUDED.sku RETURNING id''',
                (product_id,sku,row['cor'],row['modelagem'],row['preco']))
            variant_id=cur.fetchone()['id']
            cur.execute('SELECT COALESCE(MAX(sort_order),-1)+1 AS ordem FROM catalog_sizes WHERE variant_id=%s',(variant_id,))
            order=cur.fetchone()['ordem']
            measures={k:float(row[k]) for k in ['largura_cm','comprimento_cm'] if row[k] is not None}
            # Ordem legada conserva o cadastro. Duplicados reais ganham uma variante exclusiva.
            cur.execute('SELECT id FROM catalog_sizes WHERE variant_id=%s AND label=%s',(variant_id,row['tamanho']))
            if cur.fetchone():
                cur.execute('INSERT INTO catalog_variants(product_id,sku,cor,modelagem,preco) VALUES (%s,%s,%s,%s,%s) RETURNING id',
                    (product_id,sku+'-'+str(row['id']),row['cor'],row['modelagem'],row['preco']))
                variant_id=cur.fetchone()['id'];order=0
            cur.execute('INSERT INTO catalog_sizes(variant_id,label,sort_order,medidas,legacy_product_id) VALUES (%s,%s,%s,%s,%s)',
                (variant_id,row['tamanho'],order,Json(measures),row['id']))
            count+=1
    return count
