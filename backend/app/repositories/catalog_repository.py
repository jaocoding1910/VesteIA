"""Catálogo normalizado com ponte explícita para os contratos das sprints anteriores."""
from psycopg2.extras import RealDictCursor, Json
from app.database.database import conectar


def list_products():
    with conectar() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT * FROM catalog_products ORDER BY id')
        products = [dict(row) for row in cur.fetchall()]
        cur.execute('SELECT * FROM catalog_variants ORDER BY id')
        variants = [dict(row) for row in cur.fetchall()]
        cur.execute('SELECT * FROM catalog_sizes ORDER BY sort_order, id')
        sizes = [dict(row) for row in cur.fetchall()]
    for product in products:
        product['variantes'] = []
        for variant in variants:
            if variant['product_id'] != product['id']:
                continue
            variant['preco'] = float(variant['preco'] or 0)
            variant['tamanhos'] = [s for s in sizes if s['variant_id'] == variant['id']]
            product['variantes'].append(variant)
    return products


def find_product(product_id):
    return next((p for p in list_products() if p['id'] == product_id), None)


def import_product(product):
    """Upsert transacional; preserva IDs e registros legados; ordem vem da loja."""
    with conectar() as conn, conn.cursor() as cur:
        cur.execute('''INSERT INTO catalog_products(external_product_id,nome,categoria,marca,descricao,metadata)
            VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT(external_product_id) WHERE external_product_id IS NOT NULL
            DO UPDATE SET nome=EXCLUDED.nome,categoria=EXCLUDED.categoria,marca=EXCLUDED.marca,
            descricao=EXCLUDED.descricao,metadata=EXCLUDED.metadata RETURNING id''',
            (product['external_product_id'],product['nome'],product['categoria'],product.get('marca'),
             product.get('descricao'),Json(product.get('metadata',{}))))
        product_id = cur.fetchone()[0]
        for v in product['variantes']:
            cur.execute('SELECT product_id FROM catalog_variants WHERE sku=%s',(v['sku'],))
            owner=cur.fetchone()
            if owner and owner[0]!=product_id: raise ValueError('SKU já pertence a outro produto')
            cur.execute('''INSERT INTO catalog_variants(product_id,sku,cor,modelagem,preco,imagem_url,metadata)
                VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(sku) WHERE sku IS NOT NULL
                DO UPDATE SET cor=EXCLUDED.cor,modelagem=EXCLUDED.modelagem,preco=EXCLUDED.preco,
                imagem_url=EXCLUDED.imagem_url,metadata=EXCLUDED.metadata RETURNING id''',
                (product_id,v['sku'],v['cor'],v.get('modelagem','regular'),v['preco'],v.get('imagem_url'),Json(v.get('metadata',{}))))
            variant_id = cur.fetchone()[0]
            for order,s in enumerate(v['tamanhos']):
                m=s.get('medidas',{})
                cur.execute('SELECT legacy_product_id FROM catalog_sizes WHERE variant_id=%s AND label=%s',(variant_id,s['label']))
                old=cur.fetchone(); legacy_id=old[0] if old else None
                vals=(product['nome'],v['preco'],s['label'],v['cor'],product['categoria'],m.get('largura_cm'),m.get('comprimento_cm'),v.get('modelagem','regular'))
                if legacy_id:
                    cur.execute('UPDATE produtos SET nome=%s,preco=%s,tamanho=%s,cor=%s,categoria=%s,largura_cm=%s,comprimento_cm=%s,modelagem=%s WHERE id=%s',(*vals,legacy_id))
                else:
                    cur.execute('INSERT INTO produtos(nome,preco,tamanho,cor,categoria,largura_cm,comprimento_cm,modelagem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id',vals)
                    legacy_id=cur.fetchone()[0]
                cur.execute('''INSERT INTO catalog_sizes(variant_id,label,sort_order,estoque,medidas,legacy_product_id)
                    VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT(variant_id,label)
                    DO UPDATE SET sort_order=EXCLUDED.sort_order,estoque=EXCLUDED.estoque,medidas=EXCLUDED.medidas,legacy_product_id=EXCLUDED.legacy_product_id''',
                    (variant_id,s['label'],s.get('sort_order',order),s.get('estoque'),Json(m),legacy_id))
    return product_id
