from app.services.categorias_vestuario import (
    normalizar_categoria,
    obter_familia_categoria,
    obter_regiao_prioritaria,
)


def analisar_compatibilidade_corpo_produto(
    contexto_corpo_produto: dict,
):
    """
    Analisa a compatibilidade visual inicial
    entre corpo e produto no VesteIA.

    Esta camada utiliza:
    - categoria oficial da peça;
    - família estrutural da vestimenta;
    - região corporal prioritária;
    - contexto visual corporal;
    - modelagem cadastrada;
    - qualidade visual da análise.

    IMPORTANTE:

    Esta função NÃO:
    - compara medidas físicas definitivas;
    - converte geometria corporal para cm;
    - calcula folga física;
    - recomenda tamanho;
    - simula tecido;
    - afirma compatibilidade física exata.

    O resultado representa somente uma
    interpretação visual experimental.

    Sprint Multivestimenta:

    A categoria, família e região prioritária
    são obtidas da configuração central
    categorias_vestuario.py.
    """

    # ======================================================
    # VALIDAÇÃO DO CONTEXTO
    # ======================================================

    if not isinstance(
        contexto_corpo_produto,
        dict,
    ):
        return {
            "status": (
                "dados_insuficientes"
            ),

            "resultado": None,

            "categoria": None,

            "familia": None,

            "regiao_prioritaria": None,

            "confianca": {
                "nivel": (
                    "indisponivel"
                ),

                "pontuacao": None,
            },

            "uso_para_recomendacao_tamanho": (
                False
            ),

            "mensagem": (
                "Contexto corpo-produto "
                "indisponível."
            ),
        }

    status_contexto = (
        contexto_corpo_produto.get(
            "status"
        )
    )

    if (
        status_contexto
        != "pronto_para_compatibilidade"
    ):
        return {
            "status": (
                "dados_insuficientes"
            ),

            "resultado": None,

            "categoria": (
                contexto_corpo_produto.get(
                    "categoria"
                )
            ),

            "familia": (
                contexto_corpo_produto.get(
                    "familia"
                )
            ),

            "regiao_prioritaria": (
                contexto_corpo_produto.get(
                    "regiao_prioritaria"
                )
            ),

            "confianca": {
                "nivel": (
                    "indisponivel"
                ),

                "pontuacao": None,
            },

            "uso_para_recomendacao_tamanho": (
                False
            ),

            "mensagem": (
                "O contexto corpo-produto "
                "ainda não está pronto "
                "para análise."
            ),
        }

    # ======================================================
    # PRODUTO
    # ======================================================

    produto = (
        contexto_corpo_produto.get(
            "produto",
            {},
        )
        or {}
    )

    categoria_contexto = (
        contexto_corpo_produto.get(
            "categoria"
        )
        or produto.get(
            "categoria"
        )
    )

    categoria = (
        normalizar_categoria(
            categoria_contexto
        )
    )

    if categoria is None:
        return {
            "status": (
                "categoria_nao_suportada"
            ),

            "resultado": (
                "categoria_nao_suportada"
            ),

            "categoria": None,

            "familia": None,

            "regiao_prioritaria": None,

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

                "modelagem": (
                    produto.get(
                        "modelagem"
                    )
                ),
            },

            "confianca": {
                "nivel": (
                    "indisponivel"
                ),

                "pontuacao": None,
            },

            "uso_para_recomendacao_tamanho": (
                False
            ),

            "mensagem": (
                "A categoria do produto ainda "
                "não possui configuração oficial "
                "no pipeline multivestimenta."
            ),
        }

    familia = (
        contexto_corpo_produto.get(
            "familia"
        )
        or obter_familia_categoria(
            categoria
        )
    )

    regiao_prioritaria = (
        contexto_corpo_produto.get(
            "regiao_prioritaria"
        )
        or obter_regiao_prioritaria(
            categoria
        )
    )

    modelagem = (
        produto.get(
            "modelagem"
        )
    )

    tamanho = (
        produto.get(
            "tamanho"
        )
    )

    # ======================================================
    # DADOS CORPORAIS
    # ======================================================

    dados_corporais = (
        contexto_corpo_produto.get(
            "dados_corporais",
            {},
        )
        or {}
    )

    relacao_ombros_quadril = (
        dados_corporais.get(
            "relacao_ombros_quadril"
        )
    )

    # ======================================================
    # QUALIDADE VISUAL
    # ======================================================

    qualidade_visual = (
        contexto_corpo_produto.get(
            "qualidade_visual",
            {},
        )
        or {}
    )

    nivel_confianca = (
        qualidade_visual.get(
            "nivel_confianca"
        )
        or "experimental"
    )

    pontuacao_confianca = (
        qualidade_visual.get(
            "pontuacao_confianca"
        )
    )

    # ======================================================
    # MODELAGEM
    #
    # A modelagem ajuda somente na descrição
    # da tendência visual.
    #
    # Ela NÃO determina sozinha que a peça
    # seja fisicamente compatível.
    # ======================================================

    if isinstance(
        modelagem,
        str,
    ):
        modelagem_normalizada = (
            modelagem
            .strip()
            .lower()
        )

    else:
        modelagem_normalizada = ""

    if modelagem_normalizada in {
        "oversized",
        "ampla",
        "amplo",
    }:
        tendencia_modelagem = (
            "caimento_amplo"
        )

    elif modelagem_normalizada in {
        "slim",
        "ajustada",
        "ajustado",
        "justa",
        "justo",
    }:
        tendencia_modelagem = (
            "caimento_ajustado"
        )

    else:
        tendencia_modelagem = (
            "caimento_padrao"
        )

    # ======================================================
    # REFERÊNCIA CORPORAL POR FAMÍLIA
    # ======================================================

    if familia == "superior":

        referencia_corporal = {
            "regiao": (
                "tronco"
            ),

            "usa_ombros": True,

            "usa_quadril": (
                False
            ),

            "usa_pernas": (
                False
            ),

            "usa_pes": (
                False
            ),

            "relacao_ombros_quadril": (
                relacao_ombros_quadril
            ),
        }

        ajuste_estimado = (
            tendencia_modelagem
        )

        resultado = (
            "compatibilidade_em_analise"
        )

        mensagem = (
            "A análise visual da peça superior "
            "prioriza o tronco e considera "
            "a modelagem cadastrada como "
            "tendência visual de caimento."
        )

    elif familia == "inferior":

        referencia_corporal = {
            "regiao": (
                "quadril_pernas"
            ),

            "usa_ombros": (
                False
            ),

            "usa_quadril": True,

            "usa_pernas": True,

            "usa_pes": (
                False
            ),

            "relacao_ombros_quadril": (
                None
            ),
        }

        ajuste_estimado = (
            "analise_visual_preparada"
        )

        resultado = (
            "compatibilidade_em_analise"
        )

        mensagem = (
            "A análise visual da peça inferior "
            "prioriza quadril e pernas."
        )

    elif familia == "corpo_integrado":

        referencia_corporal = {
            "regiao": (
                "corpo_integrado"
            ),

            "usa_ombros": True,

            "usa_quadril": True,

            "usa_pernas": True,

            "usa_pes": (
                False
            ),

            "relacao_ombros_quadril": (
                relacao_ombros_quadril
            ),
        }

        ajuste_estimado = (
            tendencia_modelagem
        )

        resultado = (
            "compatibilidade_em_analise"
        )

        mensagem = (
            "A análise visual da peça de corpo "
            "integrado considera tronco, quadril "
            "e membros inferiores."
        )

    elif familia == "calcado":

        referencia_corporal = {
            "regiao": (
                "pes"
            ),

            "usa_ombros": (
                False
            ),

            "usa_quadril": (
                False
            ),

            "usa_pernas": (
                False
            ),

            "usa_pes": True,

            "relacao_ombros_quadril": (
                None
            ),
        }

        ajuste_estimado = (
            "analise_visual_preparada"
        )

        resultado = (
            "compatibilidade_em_analise"
        )

        mensagem = (
            "A análise visual do calçado "
            "prioriza a região dos pés."
        )

    else:

        referencia_corporal = {
            "regiao": (
                regiao_prioritaria
            ),

            "usa_ombros": (
                False
            ),

            "usa_quadril": (
                False
            ),

            "usa_pernas": (
                False
            ),

            "usa_pes": (
                False
            ),

            "relacao_ombros_quadril": (
                None
            ),
        }

        ajuste_estimado = None

        resultado = (
            "familia_nao_suportada"
        )

        mensagem = (
            "A família estrutural da peça "
            "ainda não possui regra de "
            "compatibilidade visual."
        )

    # ======================================================
    # SAÍDA FINAL
    # ======================================================

    return {
        "status": (
            "compatibilidade_analisada"
        ),

        "categoria": (
            categoria
        ),

        "familia": (
            familia
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
                tamanho
            ),

            "categoria": (
                categoria
            ),

            "modelagem": (
                modelagem
            ),
        },

        "regiao_prioritaria": (
            regiao_prioritaria
        ),

        "referencia_corporal": (
            referencia_corporal
        ),

        # Mantemos este campo por compatibilidade
        # com consumidores anteriores.
        #
        # Para famílias onde ele não faz sentido,
        # o valor será None.
        "relacao_corporal": (
            relacao_ombros_quadril
            if familia
            in {
                "superior",
                "corpo_integrado",
            }
            else None
        ),

        "ajuste_estimado": (
            ajuste_estimado
        ),

        "tendencia_modelagem": (
            tendencia_modelagem
        ),

        "resultado": (
            resultado
        ),

        "confianca": {
            "nivel": (
                nivel_confianca
            ),

            "pontuacao": (
                pontuacao_confianca
            ),
        },

        "capacidades": {
            "categoria_reconhecida": (
                True
            ),

            "familia_reconhecida": (
                familia is not None
            ),

            "analise_visual": (
                resultado
                == "compatibilidade_em_analise"
            ),

            "comparacao_fisica_cm": (
                False
            ),

            "recomendacao_tamanho": (
                False
            ),
        },

        "precisao": (
            "experimental"
        ),

        "uso_para_recomendacao_tamanho": (
            False
        ),

        "mensagem": (
            mensagem
        ),
    }