def _valor_numerico(valor):
    """
    Converte um valor para float com segurança.

    Retorna None quando o valor não puder
    ser interpretado como número positivo.
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


def _normalizar_modelagem(
    modelagem,
):
    """
    Normaliza a modelagem da peça.

    Valores internos:
    - slim
    - regular
    - oversized
    """

    if not modelagem:
        return "regular"

    modelagem = (
        str(modelagem)
        .strip()
        .lower()
    )

    mapa = {
        "slim": "slim",
        "slim_fit": "slim",
        "ajustada": "slim",
        "ajustado": "slim",

        "regular": "regular",
        "normal": "regular",
        "padrao": "regular",
        "padrão": "regular",

        "oversized": "oversized",
        "over": "oversized",
        "ampla": "oversized",
        "amplo": "oversized",
        "solta": "oversized",
        "solto": "oversized",
    }

    return mapa.get(
        modelagem,
        "regular",
    )


def _normalizar_preferencia_caimento(
    preferencia_caimento,
):
    """
    Normaliza a preferência de caimento.

    Valores internos:
    - justo
    - padrao
    - solto
    """

    if not preferencia_caimento:
        return "padrao"

    preferencia = (
        str(preferencia_caimento)
        .strip()
        .lower()
    )

    mapa = {
        "justo": "justo",
        "ajustado": "justo",
        "slim": "justo",

        "padrao": "padrao",
        "padrão": "padrao",
        "normal": "padrao",
        "regular": "padrao",

        "solto": "solto",
        "amplo": "solto",
        "oversized": "solto",
    }

    return mapa.get(
        preferencia,
        "padrao",
    )


def _extrair_metrica(
    metricas_corporais_vestuario,
    nome,
):
    """
    Obtém uma métrica corporal sem assumir
    que ela representa medida antropométrica real.
    """

    if not metricas_corporais_vestuario:
        return None

    medidas = (
        metricas_corporais_vestuario.get(
            "medidas",
            {},
        )
    )

    metrica = (
        medidas.get(
            nome,
            {},
        )
    )

    return _valor_numerico(
        metrica.get(
            "valor_cm"
        )
    )


def _obter_confianca_base(
    confianca_metrica,
):
    """
    Recupera a confiança métrica calculada
    anteriormente pelo pipeline.
    """

    if not confianca_metrica:
        return 0.0

    valor = _valor_numerico(
        confianca_metrica.get(
            "pontuacao"
        )
    )

    if valor is None:
        return 0.0

    return max(
        0.0,
        min(
            valor,
            1.0,
        ),
    )


def _avaliar_qualidade_calibracao_vestuario(
    metricas_corporais_vestuario,
    confianca_metrica,
    largura_corporal_equivalente=None,
):
    """
    Consolida a qualidade das informações
    disponíveis para calibração de vestuário.

    Não determina precisão antropométrica.
    """

    confianca_base = (
        _obter_confianca_base(
            confianca_metrica
        )
    )

    metricas_liberadas = False

    if metricas_corporais_vestuario:
        metricas_liberadas = (
            metricas_corporais_vestuario.get(
                "metricas_liberadas",
                False,
            )
        )

    largura_equivalente_disponivel = False

    if largura_corporal_equivalente:
        largura_equivalente_disponivel = (
            largura_corporal_equivalente.get(
                "disponivel",
                False,
            )
        )

    pontuacao = confianca_base

    if not metricas_liberadas:
        pontuacao *= 0.75

    if (
        largura_corporal_equivalente
        is not None
        and not largura_equivalente_disponivel
    ):
        pontuacao *= 0.85

    pontuacao = round(
        max(
            0.0,
            min(
                pontuacao,
                1.0,
            ),
        ),
        4,
    )

    if pontuacao >= 0.85:
        nivel = "alta"

    elif pontuacao >= 0.65:
        nivel = "media"

    elif pontuacao > 0:
        nivel = "baixa"

    else:
        nivel = "indisponivel"

    return {
        "nivel": nivel,

        "pontuacao": (
            pontuacao
        ),

        "metricas_vestuario_liberadas": (
            metricas_liberadas
        ),

        "largura_equivalente_disponivel": (
            largura_equivalente_disponivel
        ),
    }


def gerar_calibracao_vestuario(
    metricas_corporais_vestuario,
    confianca_metrica,
    largura_corporal_equivalente=None,
    interpretacao_corporal=None,
    modelagem=None,
    preferencia_caimento=None,
):
    """
    Consolida a camada de calibração voltada
    especificamente para vestuário.

    Responsabilidade desta camada:
    - receber métricas visuais já calculadas;
    - identificar quais métricas são observacionais;
    - identificar quais métricas podem ser usadas
      diretamente;
    - receber uma largura corporal equivalente
      experimental, quando disponível;
    - registrar modelagem e preferência de caimento;
    - produzir um contrato único para as etapas
      posteriores do VesteIA.

    IMPORTANTE:
    esta função NÃO cria uma medida antropométrica.

    Ela também NÃO altera diretamente:
    - largura do tórax;
    - largura dos ombros;
    - largura do quadril;
    - comprimento do tronco.

    A camada apenas organiza e qualifica
    essas métricas para uso no motor de vestuário.
    """

    if not metricas_corporais_vestuario:
        return {
            "status": (
                "metricas_vestuario_indisponiveis"
            ),

            "calibracao_disponivel": False,

            "comparacao_horizontal_disponivel": False,

            "comparacao_vertical_disponivel": False,

            "largura_corporal_vestuario_cm": None,

            "comprimento_corporal_vestuario_cm": None,

            "uso_para_recomendacao_tamanho": False,

            "experimental": True,

            "mensagem": (
                "Não existem métricas corporais "
                "de vestuário suficientes para "
                "iniciar a calibração."
            ),
        }

    # ======================================================
    # MÉTRICAS VISUAIS ORIGINAIS
    # ======================================================

    largura_torax_visual_cm = (
        _extrair_metrica(
            metricas_corporais_vestuario,
            "torax",
        )
    )

    largura_ombros_visual_cm = (
        _extrair_metrica(
            metricas_corporais_vestuario,
            "ombros",
        )
    )

    largura_quadril_visual_cm = (
        _extrair_metrica(
            metricas_corporais_vestuario,
            "quadril",
        )
    )

    comprimento_tronco_cm = (
        _extrair_metrica(
            metricas_corporais_vestuario,
            "tronco",
        )
    )

    # ======================================================
    # LARGURA EQUIVALENTE EXPERIMENTAL
    # ======================================================

    largura_equivalente_cm = None

    largura_equivalente_disponivel = False

    origem_largura_equivalente = None

    if largura_corporal_equivalente:

        largura_equivalente_disponivel = (
            largura_corporal_equivalente.get(
                "disponivel",
                False,
            )
        )

        if largura_equivalente_disponivel:

            largura_equivalente_cm = (
                _valor_numerico(
                    largura_corporal_equivalente.get(
                        "largura_corporal_equivalente_cm"
                    )
                )
            )

            origem_largura_equivalente = (
                largura_corporal_equivalente.get(
                    "origem"
                )
            )

    # ======================================================
    # MODELAGEM / PREFERÊNCIA
    # ======================================================

    modelagem_normalizada = (
        _normalizar_modelagem(
            modelagem
        )
    )

    preferencia_normalizada = (
        _normalizar_preferencia_caimento(
            preferencia_caimento
        )
    )

    # ======================================================
    # RELAÇÃO CORPORAL
    # ======================================================

    relacao_corporal = None

    if interpretacao_corporal:
        relacao_corporal = (
            interpretacao_corporal.get(
                "relacao_ombros_quadril"
            )
        )

    # ======================================================
    # DISPONIBILIDADE DAS DIMENSÕES
    # ======================================================

    comparacao_horizontal_disponivel = (
        largura_equivalente_disponivel
        and largura_equivalente_cm
        is not None
    )

    comparacao_vertical_disponivel = (
        comprimento_tronco_cm
        is not None
    )

    # ======================================================
    # QUALIDADE
    # ======================================================

    qualidade = (
        _avaliar_qualidade_calibracao_vestuario(
            metricas_corporais_vestuario=(
                metricas_corporais_vestuario
            ),

            confianca_metrica=(
                confianca_metrica
            ),

            largura_corporal_equivalente=(
                largura_corporal_equivalente
            ),
        )
    )

    # ======================================================
    # DIMENSÕES DISPONÍVEIS
    # ======================================================

    dimensoes_liberadas = []

    dimensoes_pendentes = []

    if comparacao_horizontal_disponivel:
        dimensoes_liberadas.append(
            "horizontal"
        )
    else:
        dimensoes_pendentes.append(
            "horizontal"
        )

    if comparacao_vertical_disponivel:
        dimensoes_liberadas.append(
            "vertical"
        )
    else:
        dimensoes_pendentes.append(
            "vertical"
        )

    # ======================================================
    # STATUS
    # ======================================================

    if (
        comparacao_horizontal_disponivel
        and comparacao_vertical_disponivel
    ):
        status = (
            "calibracao_vestuario_completa_experimental"
        )

    elif (
        comparacao_horizontal_disponivel
        or comparacao_vertical_disponivel
    ):
        status = (
            "calibracao_vestuario_parcial"
        )

    else:
        status = (
            "calibracao_vestuario_insuficiente"
        )

    calibracao_disponivel = bool(
        dimensoes_liberadas
    )

    # ======================================================
    # SEGURANÇA SEMÂNTICA
    # ======================================================

    uso_para_recomendacao_tamanho = False

    comparacao_dimensional_experimental = (
        comparacao_horizontal_disponivel
        or comparacao_vertical_disponivel
    )

    return {
        "status": (
            status
        ),

        "calibracao_disponivel": (
            calibracao_disponivel
        ),

        "modelagem": (
            modelagem_normalizada
        ),

        "preferencia_caimento": (
            preferencia_normalizada
        ),

        "relacao_corporal": (
            relacao_corporal
        ),

        "metricas_visuais_origem": {
            "largura_torax_visual_cm": (
                largura_torax_visual_cm
            ),

            "largura_ombros_visual_cm": (
                largura_ombros_visual_cm
            ),

            "largura_quadril_visual_cm": (
                largura_quadril_visual_cm
            ),

            "comprimento_tronco_visual_cm": (
                comprimento_tronco_cm
            ),
        },

        "referencias_vestuario": {
            "largura_corporal_vestuario_cm": (
                largura_equivalente_cm
            ),

            "comprimento_corporal_vestuario_cm": (
                comprimento_tronco_cm
            ),
        },

        "largura_corporal_vestuario_cm": (
            largura_equivalente_cm
        ),

        "comprimento_corporal_vestuario_cm": (
            comprimento_tronco_cm
        ),

        "comparacao_horizontal_disponivel": (
            comparacao_horizontal_disponivel
        ),

        "comparacao_vertical_disponivel": (
            comparacao_vertical_disponivel
        ),

        "dimensoes_liberadas": (
            dimensoes_liberadas
        ),

        "dimensoes_pendentes": (
            dimensoes_pendentes
        ),

        "largura_equivalente": {
            "disponivel": (
                largura_equivalente_disponivel
            ),

            "valor_cm": (
                largura_equivalente_cm
            ),

            "origem": (
                origem_largura_equivalente
            ),

            "equivalencia_antropometrica_exata": (
                False
            ),
        },

        "qualidade": (
            qualidade
        ),

        "comparacao_dimensional_experimental": (
            comparacao_dimensional_experimental
        ),

        "uso_para_recomendacao_tamanho": (
            uso_para_recomendacao_tamanho
        ),

        "experimental": True,

        "versao_calibracao": (
            "sprint_48_v1"
        ),

        "mensagem": (
            "A camada de calibração para vestuário "
            "consolidou as métricas corporais disponíveis "
            "sem tratar projeções visuais como medidas "
            "antropométricas exatas."
        ),
    }