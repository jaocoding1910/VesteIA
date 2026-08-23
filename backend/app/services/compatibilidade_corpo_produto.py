def analisar_compatibilidade_corpo_produto(
    contexto_corpo_produto: dict,
):
    """
    Primeira camada de compatibilidade
    corpo x produto do VesteIA.

    Nesta versão:
    - usa dados relativos e contexto visual;
    - não usa medidas corporais em cm
      como referência definitiva;
    - não recomenda tamanho final ainda;
    - gera uma interpretação experimental
      da peça em relação ao corpo.
    """

    if not contexto_corpo_produto:
        return {
            "status": "dados_insuficientes",
            "resultado": None,
            "confianca": "indisponivel",
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
            "status": "dados_insuficientes",
            "resultado": None,
            "confianca": "indisponivel",
            "mensagem": (
                "O contexto corpo-produto "
                "ainda não está pronto "
                "para análise."
            ),
        }

    categoria = (
        contexto_corpo_produto.get(
            "categoria"
        )
    )

    produto = (
        contexto_corpo_produto.get(
            "produto",
            {},
        )
    )

    dados_corporais = (
        contexto_corpo_produto.get(
            "dados_corporais",
            {},
        )
    )

    qualidade_visual = (
        contexto_corpo_produto.get(
            "qualidade_visual",
            {},
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

    relacao_corporal = (
        dados_corporais.get(
            "relacao_ombros_quadril"
        )
    )

    nivel_confianca = (
        qualidade_visual.get(
            "nivel_confianca"
        )
    )

    pontuacao_confianca = (
        qualidade_visual.get(
            "pontuacao_confianca"
        )
    )

    if categoria == "camiseta":
        regiao_prioritaria = "tronco"

        if (
            modelagem
            and modelagem.lower()
            == "oversized"
        ):
            ajuste_estimado = (
                "caimento_amplo"
            )

            resultado = (
                "compativel_visual"
            )

            mensagem = (
                "A peça possui modelagem "
                "oversized e tende a apresentar "
                "caimento mais amplo no tronco."
            )

        else:
            ajuste_estimado = (
                "caimento_padrao"
            )

            resultado = (
                "compatibilidade_em_analise"
            )

            mensagem = (
                "A compatibilidade visual "
                "da camiseta foi preparada "
                "para análise de caimento."
            )

    elif categoria == "calca":
        regiao_prioritaria = (
            "quadril_pernas"
        )

        ajuste_estimado = (
            "analise_visual_preparada"
        )

        resultado = (
            "compatibilidade_em_analise"
        )

        mensagem = (
            "A análise da calça prioriza "
            "quadril e pernas."
        )

    elif categoria == "vestido":
        regiao_prioritaria = (
            "corpo_integrado"
        )

        ajuste_estimado = (
            "analise_visual_preparada"
        )

        resultado = (
            "compatibilidade_em_analise"
        )

        mensagem = (
            "A análise do vestido considera "
            "tronco e membros inferiores."
        )

    elif categoria == "calcado":
        regiao_prioritaria = "pes"

        ajuste_estimado = (
            "analise_visual_preparada"
        )

        resultado = (
            "compatibilidade_em_analise"
        )

        mensagem = (
            "A análise do calçado prioriza "
            "a região dos pés."
        )

    else:
        regiao_prioritaria = None
        ajuste_estimado = None
        resultado = (
            "categoria_nao_suportada"
        )

        mensagem = (
            "A categoria do produto ainda "
            "não possui regra de "
            "compatibilidade."
        )

    return {
        "status": "compatibilidade_analisada",

        "categoria": categoria,

        "produto": {
            "id": produto.get(
                "id"
            ),
            "nome": produto.get(
                "nome"
            ),
            "tamanho": tamanho,
            "modelagem": modelagem,
        },

        "regiao_prioritaria": (
            regiao_prioritaria
        ),

        "relacao_corporal": (
            relacao_corporal
        ),

        "ajuste_estimado": (
            ajuste_estimado
        ),

        "resultado": resultado,

        "confianca": {
            "nivel": (
                nivel_confianca
                or "experimental"
            ),
            "pontuacao": (
                pontuacao_confianca
            ),
        },

        "precisao": "experimental",

        "uso_para_recomendacao_tamanho": False,

        "mensagem": mensagem,
    }