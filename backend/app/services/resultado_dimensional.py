def _valor_numerico_positivo(valor):
    """
    Converte um valor para float com segurança.

    Retorna None quando:
    - o valor não é numérico;
    - o valor é menor ou igual a zero.
    """

    if valor is None:
        return None

    try:
        valor = float(valor)

    except (
        TypeError,
        ValueError,
    ):
        return None

    if valor <= 0:
        return None

    return valor


def _classificar_largura(
    indice_relativo_largura,
):
    """
    Classifica experimentalmente
    a relação horizontal entre
    corpo e peça.

    IMPORTANTE:
    o índice não representa folga
    antropométrica real.

    Ele compara:
    largura da peça /
    referência corporal de vestuário.
    """

    if indice_relativo_largura is None:
        return "indisponivel"

    if indice_relativo_largura < 1.00:
        return "muito_justo_visual"

    if indice_relativo_largura < 1.05:
        return "justo_visual"

    if indice_relativo_largura < 1.12:
        return "regular_visual"

    if indice_relativo_largura < 1.22:
        return "amplo_visual"

    return "muito_amplo_visual"


def _classificar_comprimento(
    indice_relativo_comprimento,
):
    """
    Classifica experimentalmente
    a relação vertical entre
    corpo e peça.
    """

    if indice_relativo_comprimento is None:
        return "indisponivel"

    if indice_relativo_comprimento < 1.00:
        return "curto_visual"

    if indice_relativo_comprimento < 1.12:
        return "regular_visual"

    if indice_relativo_comprimento < 1.25:
        return "alongado_visual"

    return "muito_alongado_visual"


def _gerar_resultado_geral(
    interpretacao_largura,
    interpretacao_comprimento,
):
    """
    Consolida as interpretações
    horizontal e vertical.
    """

    largura_ampla = (
        interpretacao_largura
        in (
            "amplo_visual",
            "muito_amplo_visual",
        )
    )

    largura_justa = (
        interpretacao_largura
        in (
            "justo_visual",
            "muito_justo_visual",
        )
    )

    comprimento_alongado = (
        interpretacao_comprimento
        in (
            "alongado_visual",
            "muito_alongado_visual",
        )
    )

    comprimento_curto = (
        interpretacao_comprimento
        == "curto_visual"
    )

    if (
        largura_ampla
        and comprimento_alongado
    ):
        return (
            "caimento_amplo_e_alongado",
            (
                "A peça tende a apresentar "
                "caimento mais amplo e comprimento "
                "mais alongado no corpo."
            ),
        )

    if (
        largura_justa
        and comprimento_curto
    ):
        return (
            "caimento_justo_e_curto",
            (
                "A peça tende a apresentar "
                "caimento mais próximo ao corpo "
                "e comprimento visual mais curto."
            ),
        )

    if largura_ampla:
        return (
            "caimento_amplo",
            (
                "A peça tende a apresentar "
                "caimento mais amplo no tronco."
            ),
        )

    if largura_justa:
        return (
            "caimento_mais_justo",
            (
                "A peça tende a apresentar "
                "um caimento visual mais próximo "
                "ao corpo."
            ),
        )

    if comprimento_alongado:
        return (
            "caimento_regular_e_alongado",
            (
                "A largura tende a permanecer "
                "próxima do padrão, enquanto "
                "o comprimento tende a ficar "
                "mais alongado."
            ),
        )

    if comprimento_curto:
        return (
            "caimento_regular_e_curto",
            (
                "A largura tende a permanecer "
                "próxima do padrão, enquanto "
                "o comprimento tende a ficar "
                "visualmente mais curto."
            ),
        )

    return (
        "caimento_regular",
        (
            "A peça tende a apresentar "
            "caimento visual próximo ao padrão."
        ),
    )


def gerar_resultado_dimensional(
    compatibilidade_dimensional: dict,
):
    """
    Gera uma interpretação dimensional
    experimental a partir do contrato
    produzido pela compatibilidade dimensional.

    Arquitetura atual do VesteIA:

    1. O motor prioriza:
       medidas_referencia["vestuario"]

    2. Horizontal:
       largura_corporal_vestuario_cm

    3. Vertical:
       comprimento_corporal_vestuario_cm

    4. As medidas corporais brutas permanecem
       disponíveis apenas como fallback
       de compatibilidade durante a transição.

    IMPORTANTE:
    - não representa folga física real;
    - não representa medida antropométrica exata;
    - não libera recomendação definitiva;
    - interpreta relações dimensionais experimentais.
    """

    # ======================================================
    # 1. VALIDAÇÃO DE ENTRADA
    # ======================================================

    if not compatibilidade_dimensional:

        return {
            "status": (
                "dados_insuficientes"
            ),

            "resultado_geral": None,

            "nivel": (
                "indisponivel"
            ),

            "recomendacao_tamanho": False,

            "mensagem": (
                "Compatibilidade dimensional "
                "indisponível."
            ),
        }

    # ======================================================
    # 2. COMPLETUDE DIMENSIONAL
    # ======================================================

    comparacao_dimensional_completa = (
        compatibilidade_dimensional.get(
            "comparacao_dimensional_completa",
            False,
        )
    )

    if not comparacao_dimensional_completa:

        return {
            "status": (
                "dados_parciais"
            ),

            "resultado_geral": None,

            "nivel": (
                "experimental"
            ),

            "recomendacao_tamanho": False,

            "mensagem": (
                "Ainda não existem referências "
                "dimensionais suficientes para "
                "interpretar completamente "
                "o caimento da peça."
            ),
        }

    # ======================================================
    # 3. REFERÊNCIAS DIMENSIONAIS
    # ======================================================

    medidas_referencia = (
        compatibilidade_dimensional.get(
            "medidas_referencia",
            {},
        )
        or {}
    )

    corpo = (
        medidas_referencia.get(
            "corpo",
            {},
        )
        or {}
    )

    vestuario = (
        medidas_referencia.get(
            "vestuario",
            {},
        )
        or {}
    )

    peca = (
        medidas_referencia.get(
            "peca",
            {},
        )
        or {}
    )

    # ======================================================
    # 4. REFERÊNCIA HORIZONTAL
    # ======================================================
    #
    # PRIORIDADE:
    #
    # largura_corporal_vestuario_cm
    #
    # Fallback:
    # largura_corporal_equivalente_cm
    #
    # largura_torax_cm NÃO é utilizada
    # como primeira opção para comparação.
    # ======================================================

    largura_corporal_vestuario_cm = (
        _valor_numerico_positivo(
            vestuario.get(
                "largura_corporal_vestuario_cm"
            )
        )
    )

    origem_largura_corpo = (
        "calibracao_vestuario"
    )

    if (
        largura_corporal_vestuario_cm
        is None
    ):

        largura_corporal_vestuario_cm = (
            _valor_numerico_positivo(
                vestuario.get(
                    "largura_corporal_equivalente_cm"
                )
            )
        )

        origem_largura_corpo = (
            "largura_corporal_equivalente"
        )

    # ======================================================
    # 5. REFERÊNCIA VERTICAL
    # ======================================================

    comprimento_corporal_vestuario_cm = (
        _valor_numerico_positivo(
            vestuario.get(
                "comprimento_corporal_vestuario_cm"
            )
        )
    )

    origem_comprimento_corpo = (
        "calibracao_vestuario"
    )

    # ------------------------------------------------------
    # FALLBACK CONTROLADO
    # ------------------------------------------------------
    #
    # O comprimento do tronco é semanticamente
    # compatível com a referência vertical,
    # portanto pode ser utilizado como fallback.
    # ------------------------------------------------------

    if (
        comprimento_corporal_vestuario_cm
        is None
    ):

        comprimento_corporal_vestuario_cm = (
            _valor_numerico_positivo(
                corpo.get(
                    "comprimento_tronco_cm"
                )
            )
        )

        origem_comprimento_corpo = (
            "comprimento_tronco_corporal"
        )

    # ======================================================
    # 6. MEDIDAS DA PEÇA
    # ======================================================

    largura_peca_cm = (
        _valor_numerico_positivo(
            peca.get(
                "largura_cm"
            )
        )
    )

    comprimento_peca_cm = (
        _valor_numerico_positivo(
            peca.get(
                "comprimento_cm"
            )
        )
    )

    # ======================================================
    # 7. VALIDAÇÃO DAS QUATRO DIMENSÕES
    # ======================================================

    valores_necessarios = (
        largura_corporal_vestuario_cm,
        comprimento_corporal_vestuario_cm,
        largura_peca_cm,
        comprimento_peca_cm,
    )

    if any(
        valor is None
        for valor
        in valores_necessarios
    ):

        return {
            "status": (
                "dados_insuficientes"
            ),

            "resultado_geral": None,

            "nivel": (
                "experimental"
            ),

            "recomendacao_tamanho": False,

            "dimensoes_disponiveis": {
                "horizontal": (
                    largura_corporal_vestuario_cm
                    is not None
                    and largura_peca_cm
                    is not None
                ),

                "vertical": (
                    comprimento_corporal_vestuario_cm
                    is not None
                    and comprimento_peca_cm
                    is not None
                ),
            },

            "mensagem": (
                "As referências necessárias "
                "para interpretar horizontal "
                "e verticalmente o caimento "
                "não estão todas disponíveis."
            ),
        }

    # ======================================================
    # 8. ÍNDICES RELATIVOS
    # ======================================================

    indice_relativo_largura = (
        largura_peca_cm
        /
        largura_corporal_vestuario_cm
    )

    indice_relativo_comprimento = (
        comprimento_peca_cm
        /
        comprimento_corporal_vestuario_cm
    )

    # ======================================================
    # 9. DIFERENÇAS DIMENSIONAIS
    # ======================================================

    diferenca_visual_largura_cm = (
        largura_peca_cm
        -
        largura_corporal_vestuario_cm
    )

    diferenca_visual_comprimento_cm = (
        comprimento_peca_cm
        -
        comprimento_corporal_vestuario_cm
    )

    # ======================================================
    # 10. INTERPRETAÇÃO HORIZONTAL
    # ======================================================

    interpretacao_largura = (
        _classificar_largura(
            indice_relativo_largura
        )
    )

    # ======================================================
    # 11. INTERPRETAÇÃO VERTICAL
    # ======================================================

    interpretacao_comprimento = (
        _classificar_comprimento(
            indice_relativo_comprimento
        )
    )

    # ======================================================
    # 12. RESULTADO CONSOLIDADO
    # ======================================================

    (
        resultado_geral,
        mensagem_usuario,
    ) = _gerar_resultado_geral(
        interpretacao_largura=(
            interpretacao_largura
        ),

        interpretacao_comprimento=(
            interpretacao_comprimento
        ),
    )

    # ======================================================
    # 13. CALIBRAÇÃO / CONFIANÇA
    # ======================================================

    calibracao_vestuario = (
        compatibilidade_dimensional.get(
            "calibracao_vestuario",
            {},
        )
        or {}
    )

    confianca_metrica = (
        compatibilidade_dimensional.get(
            "confianca_metrica",
            {},
        )
        or {}
    )

    qualidade_calibracao = (
        calibracao_vestuario.get(
            "qualidade",
            {},
        )
        or {}
    )

    # ======================================================
    # 14. RESULTADO FINAL
    # ======================================================

    return {
        "status": (
            "resultado_dimensional_calculado"
        ),

        "largura": {
            "corpo_cm": round(
                largura_corporal_vestuario_cm,
                2,
            ),

            "origem_corpo": (
                origem_largura_corpo
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

            "natureza": (
                "comparacao_horizontal_vestuario_experimental"
            ),
        },

        "comprimento": {
            "corpo_cm": round(
                comprimento_corporal_vestuario_cm,
                2,
            ),

            "origem_corpo": (
                origem_comprimento_corpo
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

            "natureza": (
                "comparacao_vertical_vestuario_experimental"
            ),
        },

        "dimensoes_utilizadas": [
            "horizontal",
            "vertical",
        ],

        "referencias_utilizadas": {
            "horizontal": (
                origem_largura_corpo
            ),

            "vertical": (
                origem_comprimento_corpo
            ),
        },

        "resultado_geral": (
            resultado_geral
        ),

        "qualidade": {
            "calibracao_vestuario": (
                qualidade_calibracao.get(
                    "nivel"
                )
            ),

            "pontuacao_calibracao": (
                qualidade_calibracao.get(
                    "pontuacao"
                )
            ),

            "confianca_metrica": (
                confianca_metrica.get(
                    "nivel"
                )
            ),

            "pontuacao_confianca_metrica": (
                confianca_metrica.get(
                    "pontuacao"
                )
            ),
        },

        "nivel": (
            "experimental"
        ),

        "recomendacao_tamanho": False,

        "mensagem_usuario": (
            mensagem_usuario
        ),

        "observacao": (
            "Os índices representam comparações "
            "experimentais entre referências corporais "
            "do motor de vestuário e as dimensões "
            "cadastradas da peça. Eles não representam "
            "folga física real nem equivalência "
            "antropométrica exata."
        ),
    }