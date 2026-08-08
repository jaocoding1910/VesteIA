from app.database.database import conectar


def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT nome, preco, tamanho, cor, categoria
        FROM produtos
        """
    )

    resultados = cursor.fetchall()

    produtos = [
        {
            "nome": linha[0],
            "preco": float(linha[1]),
            "tamanho": linha[2],
            "cor": linha[3],
            "categoria": linha[4]
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
        SELECT nome, preco, tamanho, cor, categoria
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
        "nome": resultado[0],
        "preco": float(resultado[1]),
        "tamanho": resultado[2],
        "cor": resultado[3],
        "categoria": resultado[4]
    }

    return produto


def adicionar_produto(produto):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO produtos (nome, preco, tamanho, cor, categoria)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            produto.nome,
            produto.preco,
            produto.tamanho,
            produto.cor,
            produto.categoria
        )
    )

    conexao.commit()
    cursor.close()
    conexao.close()

    return produto


def atualizar_produto(id, produto):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE produtos
        SET nome = %s, preco = %s, tamanho = %s, cor = %s, categoria = %s
        WHERE id = %s
        """,
        (
            produto.nome,
            produto.preco,
            produto.tamanho,
            produto.cor,
            produto.categoria,
            id
        )
    )

    conexao.commit()
    cursor.close()
    conexao.close()

    return produto


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
        SELECT nome, preco, tamanho, cor, categoria
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
            "categoria": linha[4]
        }
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos


def buscar_produto_por_categoria_tamanho_cor(categoria, tamanho, cor):
    if categoria:
        categoria = categoria.strip()
    if tamanho:
        tamanho = tamanho.strip()
    if cor:
        cor = cor.strip()

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

    
    query = """
    SELECT nome, preco, tamanho, cor, categoria
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
            "categoria": linha[4]
        }
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos
