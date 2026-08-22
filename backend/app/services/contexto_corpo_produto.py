def normalizar_categoria_produto(categoria):
    """
    Converte a categoria cadastrada no catálogo
    para a categoria utilizada pelo pipeline corporal.
    """

    if not categoria:
        return None

    categoria_normalizada = (
        categoria
        .strip()
        .lower()
    )

    mapa_categorias = {
        "camiseta": "camiseta",
        "camisetas": "camiseta",

        "calca": "calca",
        "calcas": "calca",
        "calça": "calca",
        "calças": "calca",

        "vestido": "vestido",
        "vestidos": "vestido",

        "calcado": "calcado",
        "calcados": "calcado",
        "calçado": "calcado",
        "calçados": "calcado",
    }

    return mapa_categorias.get(
        categoria_normalizada
    )


def gerar_contexto_corpo_produto(
    produto,
    deteccao_humana,
):
    """
    Reúne dados do produto e da análise corporal.

    Não compara centímetros da peça diretamente
    com coordenadas normalizadas da imagem.
    """

    categoria_pipeline = (
        normalizar_categoria_produto(
            produto.get("categoria")
        )
    )

    if categoria_pipeline is None:
        return {
            "status": "categoria_nao_suportada",
            "categoria_produto": produto.get(
                "categoria"
            ),
            "mensagem": (
                "A categoria do produto ainda "
                "não possui mapeamento no "
                "pipeline corporal."
            ),
        }

    if not deteccao_humana.get(
        "pessoa_detectada",
        False,
    ):
        return {
            "status": (
                "dados_corporais_indisponiveis"
            ),
            "categoria": categoria_pipeline,
            "mensagem": (
                "Não existem dados corporais "
                "suficientes para relacionar "
                "corpo e produto."
            ),
        }

    vestibilidade = (
        deteccao_humana.get(
            "vestibilidade",
            {},
        )
    )

    analise_categoria = (
        vestibilidade.get(
            categoria_pipeline,
            {},
        )
    )

    confianca_analise = (
        deteccao_humana.get(
            "confianca_analise",
            {},
        ).get(
            categoria_pipeline,
            {},
        )
    )

    interpretacao_corporal = (
        deteccao_humana.get(
            "interpretacao_corporal",
            {},
        )
    )

    geometria_corporal = (
        deteccao_humana.get(
            "geometria_corporal",
            {},
        )
    )

    proporcoes_corporais = (
        deteccao_humana.get(
            "proporcoes_corporais",
            {},
        )
    )

    pronto_para_compatibilidade = (
        analise_categoria.get(
            "status"
        )
        in {
            "apta_para_analise",
            "apta_com_ressalvas",
            "analise_limitada",
        }
    )

    if pronto_para_compatibilidade:
        status = (
            "pronto_para_compatibilidade"
        )
    else:
        status = "dados_insuficientes"

    return {
        "status": status,

        "categoria": categoria_pipeline,

        "produto": {
            "id": produto.get("id"),
            "nome": produto.get("nome"),
            "tamanho": produto.get(
                "tamanho"
            ),
            "cor": produto.get("cor"),
            "modelagem": produto.get(
                "modelagem"
            ),
        },

        "medidas_peca": {
            "largura_cm": produto.get(
                "largura_cm"
            ),
            "comprimento_cm": produto.get(
                "comprimento_cm"
            ),
            "unidade": "cm",
        },

        "dados_corporais": {
            "largura_ombros_relativa": (
                geometria_corporal.get(
                    "largura_ombros"
                )
            ),
            "largura_quadril_relativa": (
                geometria_corporal.get(
                    "largura_quadril"
                )
            ),
            "proporcao_ombros_quadril": (
                proporcoes_corporais.get(
                    "proporcao_ombros_quadril"
                )
            ),
            "relacao_ombros_quadril": (
                interpretacao_corporal.get(
                    "relacao_ombros_quadril"
                )
            ),
            "unidade_geometria": (
                "coordenadas_normalizadas"
            ),
        },

        "qualidade_visual": {
            "nivel_confianca": (
                confianca_analise.get(
                    "nivel",
                    "indisponivel",
                )
            ),
            "pontuacao_confianca": (
                confianca_analise.get(
                    "pontuacao",
                    0,
                )
            ),
            "vestibilidade_visual": (
                analise_categoria.get(
                    "vestibilidade"
                )
            ),
        },

        "comparacao_fisica": {
            "status": (
                "pendente_calibracao"
            ),
            "medidas_corporais_cm": False,
        },

        "mensagem": (
            "Contexto corpo-produto preparado "
            "para futura análise "
            "de compatibilidade."
        ),
    }