from app.services.categorias_vestuario import (
    normalizar_categoria,
    obter_familia_categoria,
    obter_regiao_prioritaria,
)


def gerar_contexto_corpo_produto(
    produto,
    deteccao_humana,
):
    """
    Reúne dados do produto e da análise corporal.

    Esta camada prepara o contexto utilizado
    pelas etapas seguintes do Provador VesteIA.

    IMPORTANTE:

    Esta função NÃO:
    - compara centímetros da peça diretamente
      com coordenadas normalizadas da imagem;
    - recomenda tamanho;
    - inventa medidas corporais;
    - converte automaticamente projeções visuais
      em medidas antropométricas;
    - altera a calibração corporal.

    Sprint Multivestimenta:

    A categoria e a família estrutural da peça
    passam a ser obtidas da fonte central
    categorias_vestuario.py.
    """

    # ======================================================
    # VALIDAÇÃO DO PRODUTO
    # ======================================================

    if not isinstance(
        produto,
        dict,
    ):
        return {
            "status": "produto_invalido",
            "categoria": None,
            "familia": None,
            "mensagem": (
                "O produto recebido não possui "
                "estrutura válida para análise."
            ),
        }

    # ======================================================
    # CATEGORIA / FAMÍLIA
    # ======================================================

    categoria_original = (
        produto.get(
            "categoria"
        )
    )

    categoria_pipeline = (
        normalizar_categoria(
            categoria_original
        )
    )

    if categoria_pipeline is None:
        return {
            "status": "categoria_nao_suportada",

            "categoria_produto": (
                categoria_original
            ),

            "categoria": None,

            "familia": None,

            "mensagem": (
                "A categoria do produto ainda "
                "não possui mapeamento no "
                "pipeline multivestimenta."
            ),
        }

    familia = (
        obter_familia_categoria(
            categoria_pipeline
        )
    )

    regiao_prioritaria = (
        obter_regiao_prioritaria(
            categoria_pipeline
        )
    )

    # ======================================================
    # VALIDAÇÃO DA DETECÇÃO
    # ======================================================

    if not isinstance(
        deteccao_humana,
        dict,
    ):
        return {
            "status": (
                "dados_corporais_indisponiveis"
            ),

            "categoria": (
                categoria_pipeline
            ),

            "familia": (
                familia
            ),

            "regiao_prioritaria": (
                regiao_prioritaria
            ),

            "mensagem": (
                "A detecção corporal recebida "
                "não possui estrutura válida."
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

            "categoria": (
                categoria_pipeline
            ),

            "familia": (
                familia
            ),

            "regiao_prioritaria": (
                regiao_prioritaria
            ),

            "mensagem": (
                "Não existem dados corporais "
                "suficientes para relacionar "
                "corpo e produto."
            ),
        }

    # ======================================================
    # VESTIBILIDADE POR CATEGORIA
    # ======================================================

    vestibilidade = (
        deteccao_humana.get(
            "vestibilidade",
            {},
        )
        or {}
    )

    analise_categoria = (
        vestibilidade.get(
            categoria_pipeline,
            {},
        )
        or {}
    )

    # ======================================================
    # CONFIANÇA
    # ======================================================

    confianca_analise = (
        deteccao_humana.get(
            "confianca_analise",
            {},
        )
        or {}
    )

    confianca_categoria = (
        confianca_analise.get(
            categoria_pipeline,
            {},
        )
        or {}
    )

    # ======================================================
    # DADOS CORPORAIS
    # ======================================================

    interpretacao_corporal = (
        deteccao_humana.get(
            "interpretacao_corporal",
            {},
        )
        or {}
    )

    geometria_corporal = (
        deteccao_humana.get(
            "geometria_corporal",
            {},
        )
        or {}
    )

    proporcoes_corporais = (
        deteccao_humana.get(
            "proporcoes_corporais",
            {},
        )
        or {}
    )

    # ======================================================
    # QUALIDADE DA CATEGORIA
    # ======================================================

    status_analise_categoria = (
        analise_categoria.get(
            "status"
        )
    )

    pronto_para_compatibilidade = (
        status_analise_categoria
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
        status = (
            "dados_insuficientes"
        )

    # ======================================================
    # DADOS CORPORAIS COMUNS
    #
    # Estes dados permanecem visuais/relativos.
    #
    # A presença deles NÃO significa que todos
    # serão utilizados por todas as categorias.
    #
    # A camada dimensional posterior decidirá
    # quais métricas fazem sentido para cada peça.
    # ======================================================

    dados_corporais = {
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

        "largura_torax_relativa": (
            geometria_corporal.get(
                "largura_torax_relativa"
            )
        ),

        "comprimento_tronco_relativo": (
            geometria_corporal.get(
                "comprimento_tronco_relativo"
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

        "escala_fisica": False,
    }

    # ======================================================
    # REFERÊNCIA ESTRUTURAL DA CATEGORIA
    # ======================================================

    referencia_categoria = {
        "categoria": (
            categoria_pipeline
        ),

        "familia": (
            familia
        ),

        "regiao_prioritaria": (
            regiao_prioritaria
        ),

        "usa_tronco": (
            familia
            in {
                "superior",
                "corpo_integrado",
            }
        ),

        "usa_quadril_pernas": (
            familia
            in {
                "inferior",
                "corpo_integrado",
            }
        ),

        "usa_pes": (
            familia
            == "calcado"
        ),
    }

    # ======================================================
    # SAÍDA
    # ======================================================

    return {
        "status": (
            status
        ),

        "categoria": (
            categoria_pipeline
        ),

        "familia": (
            familia
        ),

        "regiao_prioritaria": (
            regiao_prioritaria
        ),

        "referencia_categoria": (
            referencia_categoria
        ),

        "produto": {
            "id": (
                produto.get(
                    "id"
                )
            ),

            "nome": (
                produto.get(
                    "nome"
                )
            ),

            "tamanho": (
                produto.get(
                    "tamanho"
                )
            ),

            "cor": (
                produto.get(
                    "cor"
                )
            ),

            "categoria": (
                categoria_pipeline
            ),

            "categoria_original": (
                categoria_original
            ),

            "modelagem": (
                produto.get(
                    "modelagem"
                )
            ),
        },

        # ==================================================
        # MEDIDAS CADASTRADAS DA PEÇA
        #
        # Mantemos largura/comprimento nesta Sprint para
        # compatibilidade com o banco e motores existentes.
        #
        # Depois vamos adicionar dimensões semânticas por
        # categoria sem quebrar estes campos legados.
        # ==================================================

        "medidas_peca": {
            "largura_cm": (
                produto.get(
                    "largura_cm"
                )
            ),

            "comprimento_cm": (
                produto.get(
                    "comprimento_cm"
                )
            ),

            "unidade": (
                "cm"
            ),

            "origem": (
                "catalogo_produto"
            ),
        },

        "dados_corporais": (
            dados_corporais
        ),

        "qualidade_visual": {
            "nivel_confianca": (
                confianca_categoria.get(
                    "nivel",
                    "indisponivel",
                )
            ),

            "pontuacao_confianca": (
                confianca_categoria.get(
                    "pontuacao",
                    0,
                )
            ),

            "vestibilidade_visual": (
                analise_categoria.get(
                    "vestibilidade"
                )
            ),

            "status_categoria": (
                status_analise_categoria
            ),
        },

        "comparacao_fisica": {
            "status": (
                "pendente_calibracao"
            ),

            "medidas_corporais_cm": (
                False
            ),

            "comparacao_direta_liberada": (
                False
            ),
        },

        "capacidades": {
            "contexto_multivestimenta": (
                True
            ),

            "categoria_reconhecida": (
                True
            ),

            "familia_reconhecida": (
                familia is not None
            ),

            "compatibilidade_visual_preparavel": (
                pronto_para_compatibilidade
            ),

            "comparacao_fisica_cm": (
                False
            ),
        },

        "experimental": (
            True
        ),

        "mensagem": (
            "Contexto corpo-produto preparado "
            "utilizando a categoria e a família "
            "estrutural oficiais do VesteIA."
        ),
    }