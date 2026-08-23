def gerar_decisao_provador(
    resumo_provador: dict,
    compatibilidade_corpo_produto: dict,
    compatibilidade_dimensional: dict,
    resultado_dimensional: dict,
    recomendacao_tamanho_provador: dict = None,
):
    """
    Consolida os principais resultados do VesteIA
    em um contrato final amigável para o frontend.

    Inclui:
    - qualidade da captura
    - comportamento visual da peça
    - comparação dimensional
    - sugestão experimental de tamanho
    """

    resumo_provador = (
        resumo_provador
        or {}
    )

    compatibilidade_corpo_produto = (
        compatibilidade_corpo_produto
        or {}
    )

    compatibilidade_dimensional = (
        compatibilidade_dimensional
        or {}
    )

    resultado_dimensional = (
        resultado_dimensional
        or {}
    )

    recomendacao_tamanho_provador = (
        recomendacao_tamanho_provador
        or {}
    )

    # ======================================================
    # CONTROLE DE FLUXO
    # ======================================================

    pode_continuar = (
        resumo_provador.get(
            "pode_continuar",
            False,
        )
    )

    nova_foto_necessaria = (
        resumo_provador.get(
            "nova_foto_necessaria",
            False,
        )
    )

    qualidade = (
        resumo_provador.get(
            "qualidade"
        )
        or {}
    )

    qualidade_foto = (
        qualidade.get(
            "nivel"
        )
    )

    # ======================================================
    # FOTO BLOQUEADA
    # ======================================================

    if (
        not pode_continuar
        or nova_foto_necessaria
    ):
        return {
            "status": (
                "nova_foto_necessaria"
            ),

            "pode_continuar": False,

            "titulo": (
                resumo_provador.get(
                    "titulo"
                )
                or "Precisamos de outra foto"
            ),

            "descricao": (
                resumo_provador.get(
                    "mensagem"
                )
                or (
                    "A captura atual não possui "
                    "qualidade suficiente para "
                    "continuar a análise."
                )
            ),

            "qualidade_foto": (
                qualidade_foto
            ),

            "resultado_caimento": None,

            "destaques": (
                resumo_provador.get(
                    "orientacoes",
                    [],
                )
            ),

            "confianca_visual": (
                None
            ),

            "comparacao_dimensional_completa": (
                False
            ),

            "nivel_decisao_dimensional": (
                "indisponivel"
            ),

            "recomendacao_tamanho": {
                "disponivel": False,
                "liberada": False,
                "tamanho": None,
                "status": (
                    "bloqueada_por_qualidade_captura"
                ),
                "nivel": "indisponivel",
                "pontuacao": None,
                "ranking": [],
                "alternativa": None,
            },

            "mensagem_transparencia": (
                "Envie uma nova foto antes "
                "de continuar a análise."
            ),
        }

    # ======================================================
    # RESULTADO VISUAL
    # ======================================================

    resultado_caimento = (
        resultado_dimensional.get(
            "resultado_geral"
        )
    )

    descricao = (
        resultado_dimensional.get(
            "mensagem_usuario"
        )
        or compatibilidade_corpo_produto.get(
            "mensagem"
        )
        or (
            "A análise visual da peça "
            "foi concluída."
        )
    )

    confianca = (
        compatibilidade_corpo_produto.get(
            "confianca"
        )
        or {}
    )

    confianca_visual = (
        confianca.get(
            "nivel"
        )
    )

    comparacao_dimensional_completa = (
        compatibilidade_dimensional.get(
            "comparacao_dimensional_completa",
            False,
        )
    )

    nivel_decisao_dimensional = (
        compatibilidade_dimensional.get(
            "nivel_decisao",
            "indisponivel",
        )
    )

    # ======================================================
    # DESTAQUES DO CAIMENTO
    # ======================================================

    destaques = []

    largura = (
        resultado_dimensional.get(
            "largura"
        )
        or {}
    )

    comprimento = (
        resultado_dimensional.get(
            "comprimento"
        )
        or {}
    )

    interpretacao_largura = (
        largura.get(
            "interpretacao"
        )
    )

    interpretacao_comprimento = (
        comprimento.get(
            "interpretacao"
        )
    )

    if interpretacao_largura == "muito_ajustado_visual":
        destaques.append(
            "Tende a ficar bem ajustada no tronco."
        )

    elif interpretacao_largura == "ajustado_visual":
        destaques.append(
            "Tende a ficar mais ajustada no tronco."
        )

    elif interpretacao_largura == "equilibrado_visual":
        destaques.append(
            "Tende a apresentar largura equilibrada no tronco."
        )

    elif interpretacao_largura == "amplo_visual":
        destaques.append(
            "Tende a ficar mais ampla no tronco."
        )

    elif interpretacao_largura == "muito_amplo_visual":
        destaques.append(
            "Tende a ficar bem ampla no tronco."
        )

    if interpretacao_comprimento == "curto_visual":
        destaques.append(
            "O comprimento tende a ficar mais curto."
        )

    elif interpretacao_comprimento == "regular_visual":
        destaques.append(
            "O comprimento tende a ficar equilibrado."
        )

    elif interpretacao_comprimento == "alongado_visual":
        destaques.append(
            "O comprimento tende a ficar mais alongado."
        )

    elif interpretacao_comprimento == "muito_alongado_visual":
        destaques.append(
            "O comprimento tende a ficar bem mais alongado."
        )

    # ======================================================
    # RECOMENDAÇÃO EXPERIMENTAL DE TAMANHO
    # ======================================================

    recomendacao_disponivel = (
        recomendacao_tamanho_provador.get(
            "status"
        )
        == "sugestao_tamanho_calculada"
    )

    tamanho_sugerido = (
        recomendacao_tamanho_provador.get(
            "tamanho_sugerido"
        )
    )

    pontuacao_melhor_tamanho = (
        recomendacao_tamanho_provador.get(
            "pontuacao_melhor_tamanho"
        )
    )

    ranking = (
        recomendacao_tamanho_provador.get(
            "ranking",
            [],
        )
    )

    alternativa = None

    if len(ranking) > 1:
        alternativa = {
            "tamanho": (
                ranking[1].get(
                    "tamanho"
                )
            ),

            "pontuacao": (
                ranking[1].get(
                    "pontuacao"
                )
            ),

            "resultado": (
                ranking[1].get(
                    "resultado"
                )
            ),
        }

    recomendacao_tamanho = {
        "disponivel": (
            recomendacao_disponivel
        ),

        # Ainda não consideramos a recomendação
        # antropometricamente definitiva.
        "liberada": False,

        "tamanho": (
            tamanho_sugerido
            if recomendacao_disponivel
            else None
        ),

        "status": (
            "sugestao_experimental_disponivel"
            if recomendacao_disponivel
            else "indisponivel"
        ),

        "nivel": (
            recomendacao_tamanho_provador.get(
                "nivel",
                "indisponivel",
            )
        ),

        "pontuacao": (
            pontuacao_melhor_tamanho
        ),

        "preferencia_caimento": (
            recomendacao_tamanho_provador.get(
                "preferencia_caimento"
            )
        ),

        "ranking": (
            ranking
        ),

        "alternativa": (
            alternativa
        ),

        "mensagem": (
            recomendacao_tamanho_provador.get(
                "mensagem"
            )
        ),
    }

    # ======================================================
    # TEXTO FINAL
    # ======================================================

    if recomendacao_disponivel:
        titulo = (
            "Veja como essa peça tende a vestir "
            "e qual tamanho apresentou "
            "o melhor equilíbrio"
        )

        mensagem_transparencia = (
            recomendacao_tamanho_provador.get(
                "mensagem_transparencia"
            )
            or (
                "A sugestão de tamanho utiliza "
                "medidas visuais experimentais "
                "e ainda não representa uma "
                "recomendação antropométrica definitiva."
            )
        )

    else:
        titulo = (
            "Veja como essa peça tende "
            "a vestir em você"
        )

        mensagem_transparencia = (
            "A análise atual utiliza estimativas "
            "visuais e ainda não representa uma "
            "recomendação definitiva de tamanho."
        )

    return {
        "status": (
            "analise_consolidada"
        ),

        "pode_continuar": True,

        "titulo": (
            titulo
        ),

        "descricao": (
            descricao
        ),

        "qualidade_foto": (
            qualidade_foto
        ),

        "resultado_caimento": (
            resultado_caimento
        ),

        "destaques": (
            destaques
        ),

        "confianca_visual": (
            confianca_visual
        ),

        "comparacao_dimensional_completa": (
            comparacao_dimensional_completa
        ),

        "nivel_decisao_dimensional": (
            nivel_decisao_dimensional
        ),

        "recomendacao_tamanho": (
            recomendacao_tamanho
        ),

        "mensagem_transparencia": (
            mensagem_transparencia
        ),
    }