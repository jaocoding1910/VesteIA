def gerar_resultado_dimensional(
    compatibilidade_dimensional: dict,
):
    """
    Gera uma interpretação dimensional experimental
    a partir das medidas corpo x peça.

    Importante:
    - não representa folga física real;
    - não libera recomendação final de tamanho;
    - trabalha com índices relativos de caimento;
    - depende de medidas visuais experimentais.
    """

    if not compatibilidade_dimensional:
        return {
            "status": "dados_insuficientes",
            "resultado_geral": None,
            "nivel": "indisponivel",
            "mensagem": (
                "Compatibilidade dimensional "
                "indisponível."
            ),
        }

    if not compatibilidade_dimensional.get(
        "comparacao_dimensional_completa",
        False,
    ):
        return {
            "status": "dados_parciais",
            "resultado_geral": None,
            "nivel": "experimental",
            "mensagem": (
                "Ainda não existem medidas "
                "suficientes para interpretar "
                "o caimento dimensional."
            ),
        }

    medidas_referencia = (
        compatibilidade_dimensional.get(
            "medidas_referencia",
            {},
        )
    )

    corpo = medidas_referencia.get(
        "corpo",
        {},
    )

    peca = medidas_referencia.get(
        "peca",
        {},
    )

    largura_torax_cm = corpo.get(
        "largura_torax_cm"
    )

    comprimento_tronco_cm = corpo.get(
        "comprimento_tronco_cm"
    )

    largura_peca_cm = peca.get(
        "largura_cm"
    )

    comprimento_peca_cm = peca.get(
        "comprimento_cm"
    )

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    valores_necessarios = (
        largura_torax_cm,
        comprimento_tronco_cm,
        largura_peca_cm,
        comprimento_peca_cm,
    )

    if any(
        valor is None
        for valor in valores_necessarios
    ):
        return {
            "status": "dados_insuficientes",
            "resultado_geral": None,
            "nivel": "experimental",
            "mensagem": (
                "As medidas necessárias para "
                "interpretar o caimento não estão "
                "todas disponíveis."
            ),
        }

    if (
        largura_torax_cm <= 0
        or comprimento_tronco_cm <= 0
    ):
        return {
            "status": "medidas_invalidas",
            "resultado_geral": None,
            "nivel": "experimental",
            "mensagem": (
                "As medidas corporais disponíveis "
                "não são válidas para comparação."
            ),
        }

    # ======================================================
    # ÍNDICES RELATIVOS
    # ======================================================

    indice_relativo_largura = (
        largura_peca_cm
        / largura_torax_cm
    )

    indice_relativo_comprimento = (
        comprimento_peca_cm
        / comprimento_tronco_cm
    )

    diferenca_visual_largura_cm = (
        largura_peca_cm
        - largura_torax_cm
    )

    diferenca_visual_comprimento_cm = (
        comprimento_peca_cm
        - comprimento_tronco_cm
    )

    # ======================================================
    # INTERPRETAÇÃO DA LARGURA
    # ======================================================

    if indice_relativo_largura < 1.00:
        interpretacao_largura = (
            "muito_justo_visual"
        )

    elif indice_relativo_largura < 1.05:
        interpretacao_largura = (
            "justo_visual"
        )

    elif indice_relativo_largura < 1.12:
        interpretacao_largura = (
            "regular_visual"
        )

    elif indice_relativo_largura < 1.22:
        interpretacao_largura = (
            "amplo_visual"
        )

    else:
        interpretacao_largura = (
            "muito_amplo_visual"
        )

    # ======================================================
    # INTERPRETAÇÃO DO COMPRIMENTO
    # ======================================================

    if indice_relativo_comprimento < 1.00:
        interpretacao_comprimento = (
            "curto_visual"
        )

    elif indice_relativo_comprimento < 1.12:
        interpretacao_comprimento = (
            "regular_visual"
        )

    elif indice_relativo_comprimento < 1.25:
        interpretacao_comprimento = (
            "alongado_visual"
        )

    else:
        interpretacao_comprimento = (
            "muito_alongado_visual"
        )

    # ======================================================
    # RESULTADO GERAL
    # ======================================================

    if (
        interpretacao_largura
        in (
            "amplo_visual",
            "muito_amplo_visual",
        )
        and
        interpretacao_comprimento
        in (
            "alongado_visual",
            "muito_alongado_visual",
        )
    ):
        resultado_geral = (
            "caimento_amplo_e_alongado"
        )

        mensagem_usuario = (
            "A peça tende a apresentar "
            "caimento mais amplo e comprimento "
            "mais alongado no corpo."
        )

    elif (
        interpretacao_largura
        in (
            "amplo_visual",
            "muito_amplo_visual",
        )
    ):
        resultado_geral = (
            "caimento_amplo"
        )

        mensagem_usuario = (
            "A peça tende a apresentar "
            "caimento mais amplo no tronco."
        )

    elif (
        interpretacao_largura
        in (
            "justo_visual",
            "muito_justo_visual",
        )
    ):
        resultado_geral = (
            "caimento_mais_justo"
        )

        mensagem_usuario = (
            "A peça tende a apresentar "
            "um caimento visual mais próximo "
            "ao corpo."
        )

    else:
        resultado_geral = (
            "caimento_regular"
        )

        mensagem_usuario = (
            "A peça tende a apresentar "
            "caimento visual próximo ao padrão."
        )

    # ======================================================
    # RESULTADO
    # ======================================================

    return {
        "status": "resultado_dimensional_calculado",

        "largura": {
            "corpo_cm": round(
                largura_torax_cm,
                2,
            ),
            "peca_cm": round(
                largura_peca_cm,
                2,
            ),
            "diferenca_visual_cm": round(
                diferenca_visual_largura_cm,
                2,
            ),
            "indice_relativo_caimento": round(
                indice_relativo_largura,
                4,
            ),
            "interpretacao": (
                interpretacao_largura
            ),
        },

        "comprimento": {
            "corpo_cm": round(
                comprimento_tronco_cm,
                2,
            ),
            "peca_cm": round(
                comprimento_peca_cm,
                2,
            ),
            "diferenca_visual_cm": round(
                diferenca_visual_comprimento_cm,
                2,
            ),
            "indice_relativo_comprimento": round(
                indice_relativo_comprimento,
                4,
            ),
            "interpretacao": (
                interpretacao_comprimento
            ),
        },

        "resultado_geral": (
            resultado_geral
        ),

        "nivel": "experimental",

        "recomendacao_tamanho": False,

        "mensagem_usuario": (
            mensagem_usuario
        ),

        "observacao": (
            "Os índices representam comparação "
            "visual experimental entre corpo e peça "
            "e não equivalem a folga física real."
        ),
    }