from app.database.database import conectar


def _converter_linha_para_produto(linha):
    """
    Converte uma linha retornada pelo PostgreSQL
    em um dicionário padronizado de produto.

    Ordem esperada da consulta:
    id, nome, preco, tamanho, cor, categoria,
    largura_cm, comprimento_cm, modelagem.
    """

    return {
        "id": linha[0],
        "nome": linha[1],
        "preco": float(linha[2]),
        "tamanho": linha[3],
        "cor": linha[4],
        "categoria": linha[5],
        "largura_cm": (
            float(linha[6])
            if linha[6] is not None
            else None
        ),
        "comprimento_cm": (
            float(linha[7])
            if linha[7] is not None
            else None
        ),
        "modelagem": linha[8],
    }


def listar_produtos():
    """
    Retorna todos os produtos cadastrados no PostgreSQL.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nome,
            preco,
            tamanho,
            cor,
            categoria,
            largura_cm,
            comprimento_cm,
            modelagem
        FROM produtos
        ORDER BY id
        """
    )

    resultados = cursor.fetchall()

    produtos = [
        _converter_linha_para_produto(linha)
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos


def buscar_produto_por_id(id):
    """
    Busca um produto específico utilizando sua chave primária.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nome,
            preco,
            tamanho,
            cor,
            categoria,
            largura_cm,
            comprimento_cm,
            modelagem
        FROM produtos
        WHERE id = %s
        """,
        (id,),
    )

    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    if resultado is None:
        return None

    return _converter_linha_para_produto(resultado)


def adicionar_produto(produto):
    """
    Insere um novo produto no PostgreSQL e retorna
    o produto completo com o ID gerado pelo banco.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO produtos (
            nome,
            preco,
            tamanho,
            cor,
            categoria,
            largura_cm,
            comprimento_cm,
            modelagem
        )
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
            produto.modelagem,
        ),
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
        "modelagem": produto.modelagem,
    }


def atualizar_produto(id, produto):
    """
    Atualiza completamente um produto existente.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE produtos
        SET
            nome = %s,
            preco = %s,
            tamanho = %s,
            cor = %s,
            categoria = %s,
            largura_cm = %s,
            comprimento_cm = %s,
            modelagem = %s
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
            id,
        ),
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
        "modelagem": produto.modelagem,
    }


def deletar_produto(id):
    """
    Remove um produto do PostgreSQL utilizando seu ID.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM produtos
        WHERE id = %s
        """,
        (id,),
    )

    conexao.commit()
    cursor.close()
    conexao.close()


def buscar_produto_por_categoria(categoria):
    """
    Busca produtos cuja categoria contenha o texto informado.

    A comparação ignora diferenças entre maiúsculas,
    minúsculas e acentos.
    """

    categoria = categoria.strip()

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nome,
            preco,
            tamanho,
            cor,
            categoria,
            largura_cm,
            comprimento_cm,
            modelagem
        FROM produtos
        WHERE unaccent(categoria) ILIKE unaccent(%s)
        ORDER BY id
        """,
        (f"%{categoria}%",),
    )

    resultados = cursor.fetchall()

    produtos = [
        _converter_linha_para_produto(linha)
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos


def buscar_produto_por_categoria_tamanho_cor(
    categoria=None,
    tamanho=None,
    cor=None,
    largura_cm=None,
    comprimento_cm=None,
    modelagem=None,
):
    """
    Busca produtos utilizando filtros opcionais.

    Somente os filtros efetivamente informados são
    adicionados à consulta SQL.
    """

    if categoria:
        categoria = categoria.strip()

    if tamanho:
        tamanho = tamanho.strip()

    if cor:
        cor = cor.strip()

    if largura_cm is not None:
        largura_cm = float(largura_cm)

    if comprimento_cm is not None:
        comprimento_cm = float(comprimento_cm)

    if modelagem:
        modelagem = modelagem.strip()

    conexao = conectar()
    cursor = conexao.cursor()

    condicoes = []
    parametros = []

    # Monta dinamicamente apenas os filtros recebidos.
    if categoria:
        condicoes.append(
            "unaccent(categoria) ILIKE unaccent(%s)"
        )
        parametros.append(f"%{categoria}%")

    if tamanho:
        condicoes.append(
            "unaccent(tamanho) ILIKE unaccent(%s)"
        )
        parametros.append(f"%{tamanho}%")

    if cor:
        condicoes.append(
            "unaccent(cor) ILIKE unaccent(%s)"
        )
        parametros.append(f"%{cor}%")

    if largura_cm is not None:
        condicoes.append("largura_cm = %s")
        parametros.append(largura_cm)

    if comprimento_cm is not None:
        condicoes.append("comprimento_cm = %s")
        parametros.append(comprimento_cm)

    if modelagem:
        condicoes.append(
            "unaccent(modelagem) ILIKE unaccent(%s)"
        )
        parametros.append(f"%{modelagem}%")

    query = """
        SELECT
            id,
            nome,
            preco,
            tamanho,
            cor,
            categoria,
            largura_cm,
            comprimento_cm,
            modelagem
        FROM produtos
    """

    if condicoes:
        query += " WHERE " + " AND ".join(condicoes)

    query += " ORDER BY id"

    cursor.execute(
        query,
        tuple(parametros),
    )

    resultados = cursor.fetchall()

    produtos = [
        _converter_linha_para_produto(linha)
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos


def buscar_variacoes_produto(
    produto_referencia: dict,
):
    """
    Busca todas as variações de tamanho
    equivalentes ao produto informado.

    Nesta versão consideramos como pertencentes
    ao mesmo produto os registros que possuem:

    - mesmo nome
    - mesma cor
    - mesma categoria
    - mesma modelagem

    O tamanho pode variar.

    Esse conjunto será utilizado pelo VesteIA
    para comparar P, M, G, GG etc.
    """

    if not produto_referencia:
        return []

    nome = produto_referencia.get(
        "nome"
    )

    cor = produto_referencia.get(
        "cor"
    )

    categoria = produto_referencia.get(
        "categoria"
    )

    modelagem = produto_referencia.get(
        "modelagem"
    )

    if not nome:
        return []

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nome,
            preco,
            tamanho,
            cor,
            categoria,
            largura_cm,
            comprimento_cm,
            modelagem
        FROM produtos
        WHERE
            unaccent(nome) = unaccent(%s)
            AND unaccent(cor) = unaccent(%s)
            AND unaccent(categoria) = unaccent(%s)
            AND unaccent(modelagem) = unaccent(%s)
        ORDER BY id
        """,
        (
            nome,
            cor,
            categoria,
            modelagem,
        ),
    )

    resultados = (
        cursor.fetchall()
    )

    produtos = [
        _converter_linha_para_produto(
            linha
        )
        for linha in resultados
    ]

    cursor.close()
    conexao.close()

    return produtos

# ==========================================================
# GRADE DINÂMICA DE VARIANTES
# ==========================================================
#
# REGRA ARQUITETURAL:
#
# O VesteIA não possui uma grade universal de tamanhos.
#
# A grade é descoberta a partir das variantes realmente
# existentes no catálogo da loja.
#
# Exemplos válidos:
#
# PP, P, M, G, GG, EXG, GG2
# 34, 36, 38, 40, 42, 44, 46
# XS, S, M, L, XL, 2XL, 3XL
# Único
#
# O nome original informado pelo comércio é preservado.
#
# Nesta etapa do MVP, a ordem das variantes acompanha
# a ordem em que elas foram cadastradas no banco (id).
#
# Em uma integração produtiva, essa ordem poderá ser
# recebida diretamente do catálogo/ERP/API da loja por
# meio de um campo como ordem_grade.
# ==========================================================


def obter_grade_tamanhos_produto(
    produto_referencia: dict,
):
    """
    Retorna os tamanhos realmente existentes
    para um determinado produto.

    A grade é construída dinamicamente a partir
    das variantes encontradas no catálogo.

    O VesteIA:

    - não exige P/M/G/GG;
    - não converte GG2 para 3XL;
    - não inventa tamanhos ausentes;
    - preserva a nomenclatura original da loja.
    """

    variacoes = buscar_variacoes_produto(
        produto_referencia
    )

    grade = []

    for variacao in variacoes:

        tamanho = variacao.get(
            "tamanho"
        )

        if tamanho is None:
            continue

        tamanho = str(
            tamanho
        ).strip()

        if not tamanho:
            continue

        if tamanho not in grade:
            grade.append(
                tamanho
            )

    return grade


def obter_variantes_produto(
    produto_referencia: dict,
):
    """
    Retorna as variantes disponíveis
    preservando os dados cadastrados
    pelo catálogo da loja.

    O tamanho é tratado como identificador
    externo da variante, e não como enumeração
    fixa do VesteIA.
    """

    variacoes = buscar_variacoes_produto(
        produto_referencia
    )

    variantes = []

    for indice, variacao in enumerate(
        variacoes,
        start=1,
    ):

        tamanho = variacao.get(
            "tamanho"
        )

        if tamanho is not None:
            tamanho = str(
                tamanho
            ).strip()

        variantes.append(
            {
                "id": variacao.get(
                    "id"
                ),

                "tamanho": (
                    tamanho
                ),

                # Ordem demonstrativa derivada
                # da sequência retornada pelo banco.
                #
                # Futuramente poderá vir diretamente
                # da integração da loja.
                "ordem_grade": (
                    indice
                ),

                "preco": variacao.get(
                    "preco"
                ),

                "largura_cm": variacao.get(
                    "largura_cm"
                ),

                "comprimento_cm": variacao.get(
                    "comprimento_cm"
                ),

                "modelagem": variacao.get(
                    "modelagem"
                ),

                "cor": variacao.get(
                    "cor"
                ),

                "categoria": variacao.get(
                    "categoria"
                ),
            }
        )

    return variantes


def montar_catalogo_variantes_produto(
    produto_referencia: dict,
):
    """
    Monta uma visão consolidada do produto
    com sua grade dinâmica e suas variantes.

    Essa estrutura servirá como ponte entre:

    catálogo da loja
        ↓
    normalização VesteIA
        ↓
    motor de recomendação

    A função não recomenda tamanho.
    Apenas descreve o que realmente existe
    no catálogo para aquele produto.
    """

    if not produto_referencia:
        return {
            "produto": None,
            "grade_tamanhos": [],
            "variantes": [],
            "grade_dinamica": True,
        }

    variantes = obter_variantes_produto(
        produto_referencia
    )

    grade_tamanhos = [
        variante.get(
            "tamanho"
        )
        for variante in variantes
        if variante.get(
            "tamanho"
        )
    ]

    return {
        "produto": {
            "id_referencia": (
                produto_referencia.get(
                    "id"
                )
            ),

            "nome": (
                produto_referencia.get(
                    "nome"
                )
            ),

            "cor": (
                produto_referencia.get(
                    "cor"
                )
            ),

            "categoria": (
                produto_referencia.get(
                    "categoria"
                )
            ),

            "modelagem": (
                produto_referencia.get(
                    "modelagem"
                )
            ),
        },

        "grade_tamanhos": (
            grade_tamanhos
        ),

        "variantes": (
            variantes
        ),

        "quantidade_variantes": (
            len(
                variantes
            )
        ),

        "grade_dinamica": True,

        "tamanho_padrao_vesteia": False,

        "origem_grade": (
            "catalogo_produto"
        ),
    }

