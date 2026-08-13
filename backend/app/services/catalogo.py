from app.database.database import conectar


def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id, nome, preco, tamanho, cor, categoria, largura_cm, comprimento_cm, modelagem
        FROM produtos
        """
    )

    resultados = cursor.fetchall()

    produtos = [
        {

            "id": linha[0],
            "nome": linha[1],
            "preco": float(linha[2]),
            "tamanho": linha[3],
            "cor": linha[4],
            "categoria": linha[5],
            "largura_cm": float(linha[6]) if linha[6] is not None else None,
            "comprimento_cm": float(linha[7]) if linha[7] is not None else None,
            "modelagem": linha[8]
        }
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos


def buscar_produto_por_id(id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id, nome, preco, tamanho, cor, categoria, largura_cm, comprimento_cm, modelagem
        FROM produtos
        WHERE id = %s
        """,
        (id,)
    )

    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    if resultado is None:
        return None

    produto = {
        "id": resultado[0],
        "nome": resultado[1],
        "preco": float(resultado[2]),
        "tamanho": resultado[3],
        "cor": resultado[4],
        "categoria": resultado[5],
        "largura_cm": float(resultado[6]) if resultado[6] is not None else None,
        "comprimento_cm": float(resultado[7]) if resultado[7] is not None else None,
        "modelagem": resultado[8]
    }

    return produto


def adicionar_produto(produto):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO produtos (nome, preco, tamanho, cor, categoria, largura_cm, comprimento_cm, modelagem)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            produto.nome,
            produto.preco,
            produto.tamanho,
            produto.cor,
            produto.categoria,
            produto.largura_cm,
            produto.comprimento_cm,
            produto.modelagem
        )
    )

    novo_id = cursor.fetchone()[0]

    conexao.commit()
    cursor.close()
    conexao.close()

    return {
        "id": novo_id,
        "nome": produto.nome,
        "preco": produto.preco,
        "tamanho": produto.tamanho,
        "cor": produto.cor,
        "categoria": produto.categoria,
        "largura_cm": produto.largura_cm,
        "comprimento_cm": produto.comprimento_cm,
        "modelagem": produto.modelagem
    }


def atualizar_produto(id, produto):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE produtos
        SET nome = %s, preco = %s, tamanho = %s, cor = %s, categoria = %s, largura_cm = %s, comprimento_cm = %s, modelagem = %s
        WHERE id = %s
        """,
        (
            produto.nome,
            produto.preco,
            produto.tamanho,
            produto.cor,
            produto.categoria,
            produto.largura_cm,
            produto.comprimento_cm,
            produto.modelagem,
            id
        )
    )

    conexao.commit()
    cursor.close()
    conexao.close()

    return {
        "id": id,
        "nome": produto.nome,
        "preco": produto.preco,
        "tamanho": produto.tamanho,
        "cor": produto.cor,
        "categoria": produto.categoria,
        "largura_cm": produto.largura_cm,
        "comprimento_cm": produto.comprimento_cm,
        "modelagem": produto.modelagem
    }


def deletar_produto(id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM produtos
        WHERE id = %s
        """,
        (id,)
    )

    conexao.commit()
    cursor.close()
    conexao.close()


def buscar_produto_por_categoria(categoria):
    categoria = categoria.strip()

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT nome, preco, tamanho, cor, categoria, largura_cm, comprimento_cm, modelagem
        FROM produtos
        WHERE unaccent(categoria) ILIKE unaccent(%s)
        """,
        (f"%{categoria}%",)
    )

    resultados = cursor.fetchall()

    produtos = [
        {
            "nome": linha[0],
            "preco": float(linha[1]),
            "tamanho": linha[2],
            "cor": linha[3],
            "categoria": linha[4],
            "largura_cm": float(linha[5]) if linha[5] is not None else None,
            "comprimento_cm": float(linha[6]) if linha[6] is not None else None,
            "modelagem": linha[7]
        }
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos


def buscar_produto_por_categoria_tamanho_cor(categoria, tamanho, cor, largura_cm, comprimento_cm, modelagem):
    if categoria:
        categoria = categoria.strip()
    if tamanho:
        tamanho = tamanho.strip()
    if cor:
        cor = cor.strip()
    if largura_cm:
        largura_cm = float(largura_cm)
    if comprimento_cm:
        comprimento_cm = float(comprimento_cm)
    if modelagem:
        modelagem = modelagem.strip()

    conexao = conectar()
    cursor = conexao.cursor()

    condicoes = []
    parametros = []

    if categoria:
        condicoes.append("unaccent(categoria) ILIKE unaccent(%s)")
        parametros.append(f"%{categoria}%")

    if tamanho:
        condicoes.append("unaccent(tamanho) ILIKE unaccent(%s)")
        parametros.append(f"%{tamanho}%")

    if cor:
        condicoes.append("unaccent(cor) ILIKE unaccent(%s)")
        parametros.append(f"%{cor}%")

    if largura_cm:
        condicoes.append("largura_cm = %s")
        parametros.append(largura_cm)

    if comprimento_cm:
        condicoes.append("comprimento_cm = %s")
        parametros.append(comprimento_cm)

    if modelagem:
        condicoes.append("unaccent(modelagem) ILIKE unaccent(%s)")
        parametros.append(f"%{modelagem}%")
    
    query = """
    SELECT nome, preco, tamanho, cor, categoria, largura_cm, comprimento_cm, modelagem
    FROM produtos
    """
    if condicoes:
        query += " WHERE " + " AND ".join(condicoes)

    cursor.execute(query, tuple(parametros))
    resultados = cursor.fetchall()

    produtos = [
        {
            "nome": linha[0],
            "preco": float(linha[1]),
            "tamanho": linha[2],
            "cor": linha[3],
            "categoria": linha[4],
            "largura_cm": float(linha[5]) if linha[5] is not None else None,
            "comprimento_cm": float(linha[6]) if linha[6] is not None else None,
            "modelagem": linha[7]
        }
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos