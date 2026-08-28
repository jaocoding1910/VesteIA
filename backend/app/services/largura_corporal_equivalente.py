def _valor_numerico(valor):
    """
    Converte um valor para float com segurança.

    Retorna None quando o valor não puder
    ser interpretado numericamente.
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
        "ajustada": "slim",
        "ajustado": "slim",

        "regular": "regular",
        "normal": "regular",
        "padrao": "regular",
        "padrão": "regular",

        "oversized": "oversized",
        "ampla": "oversized",
        "amplo": "oversized",
        "solta": "oversized",
        "solto": "oversized",
    }

    return mapa.get(
        modelagem,
        "regular",
    )


def _calcular_confianca_largura_equivalente(
    confianca_metrica,
    metricas_corporais_vestuario,
):
    """
    Calcula uma confiança específica
    para a largura corporal equivalente.

    Essa confiança não representa
    precisão antropométrica real.
    """

    pontuacao_base = 0.0

    if confianca_metrica:
        pontuacao_base = (
            _valor_numerico(
                confianca_metrica.get(
                    "pontuacao"
                )
            )
            or 0.0
        )

    metricas_liberadas = (
        metricas_corporais_vestuario.get(
            "metricas_liberadas",
            False,
        )
        if metricas_corporais_vestuario
        else False
    )

    if not metricas_liberadas:
        pontuacao_base *= 0.70

    pontuacao = max(
        0.0,
        min(
            pontuacao_base,
            1.0,
        ),
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
        "pontuacao": round(
            pontuacao,
            4,
        ),
    }


def gerar_largura_corporal_equivalente(
    metricas_corporais_vestuario,
    confianca_metrica,
    interpretacao_corporal=None,
    modelagem=None,
):
    """
    Gera uma referência horizontal experimental
    para comparação com a largura da peça.

    IMPORTANTE:
    esta função NÃO transforma diretamente
    a largura visual do tórax em uma medida
    antropométrica real.

    A saída representa uma métrica derivada
    de vestuário, construída a partir de:
    - projeção frontal do tórax;
    - largura observada dos ombros;
    - relação corporal;
    - modelagem da peça;
    - confiança métrica do pipeline.

    O objetivo é permitir comparação experimental
    com largura_cm da peça sem afirmar equivalência
    física absoluta.
    """

    if not metricas_corporais_vestuario:
        return {
            "status": (
                "metricas_vestuario_indisponiveis"
            ),

            "disponivel": False,

            "largura_corporal_equivalente_cm": (
                None
            ),

            "confianca": {
                "nivel": "indisponivel",
                "pontuacao": 0,
            },

            "uso_para_recomendacao_tamanho": (
                False
            ),
        }

    medidas = (
        metricas_corporais_vestuario.get(
            "medidas",
            {},
        )
    )

    torax = (
        medidas.get(
            "torax",
            {}
        )
    )

    ombros = (
        medidas.get(
            "ombros",
            {}
        )
    )

    largura_torax_cm = (
        _valor_numerico(
            torax.get(
                "valor_cm"
            )
        )
    )

    largura_ombros_cm = (
        _valor_numerico(
            ombros.get(
                "valor_cm"
            )
        )
    )

    if (
        largura_torax_cm is None
        or largura_ombros_cm is None
    ):
        return {
            "status": (
                "metricas_horizontais_insuficientes"
            ),

            "disponivel": False,

            "largura_corporal_equivalente_cm": (
                None
            ),

            "confianca": {
                "nivel": "indisponivel",
                "pontuacao": 0,
            },

            "uso_para_recomendacao_tamanho": (
                False
            ),

            "mensagem": (
                "Não existem métricas horizontais "
                "suficientes para estimar uma "
                "largura corporal equivalente."
            ),
        }

    modelagem_normalizada = (
        _normalizar_modelagem(
            modelagem
        )
    )

    relacao_corporal = None

    if interpretacao_corporal:
        relacao_corporal = (
            interpretacao_corporal.get(
                "relacao_ombros_quadril"
            )
        )

    # ======================================================
    # 1. REFERÊNCIA HORIZONTAL BASE
    # ======================================================
    #
    # A largura equivalente não é igual
    # à projeção visual do tórax.
    #
    # Utilizamos uma composição entre:
    # - tórax frontal observado;
    # - ombros observados.
    #
    # Os pesos continuam experimentais.
    # ======================================================

    peso_torax = 0.70
    peso_ombros = 0.30

    largura_base = (
        (
            largura_torax_cm
            * peso_torax
        )
        +
        (
            largura_ombros_cm
            * peso_ombros
        )
    )

    # ======================================================
    # 2. AJUSTE PELA RELAÇÃO CORPORAL
    # ======================================================

    fator_corporal = 1.0

    if (
        relacao_corporal
        == "ombros_mais_largos"
    ):
        fator_corporal = 1.03

    elif (
        relacao_corporal
        == "quadril_mais_largo"
    ):
        fator_corporal = 0.99

    # ======================================================
    # 3. AJUSTE DA REFERÊNCIA POR MODELAGEM
    # ======================================================
    #
    # A modelagem NÃO altera o corpo.
    #
    # Ela altera apenas o alvo experimental
    # de espaço horizontal desejado para
    # comparação com a peça.
    # ======================================================

    fatores_modelagem = {
        "slim": 0.98,
        "regular": 1.00,
        "oversized": 1.04,
    }

    fator_modelagem = (
        fatores_modelagem[
            modelagem_normalizada
        ]
    )

    largura_equivalente = (
        largura_base
        * fator_corporal
        * fator_modelagem
    )

    # ======================================================
    # 4. PLAUSIBILIDADE INTERNA
    # ======================================================

    largura_equivalente = round(
        largura_equivalente,
        2,
    )

    plausivel = (
        20.0
        <= largura_equivalente
        <= 70.0
    )

    confianca = (
        _calcular_confianca_largura_equivalente(
            confianca_metrica=(
                confianca_metrica
            ),
            metricas_corporais_vestuario=(
                metricas_corporais_vestuario
            ),
        )
    )

    confianca_suficiente = (
        confianca.get(
            "nivel"
        )
        in (
            "alta",
            "media",
        )
    )

    disponivel = (
        plausivel
        and confianca_suficiente
    )

    if disponivel:
        status = (
            "largura_equivalente_calculada"
        )

    elif not plausivel:
        status = (
            "largura_equivalente_implausivel"
        )

    else:
        status = (
            "largura_equivalente_com_baixa_confianca"
        )

    return {
        "status": (
            status
        ),

        "disponivel": (
            disponivel
        ),

        "largura_corporal_equivalente_cm": (
            largura_equivalente
            if plausivel
            else None
        ),

        "componentes": {
            "largura_torax_visual_cm": round(
                largura_torax_cm,
                2,
            ),

            "largura_ombros_visual_cm": round(
                largura_ombros_cm,
                2,
            ),

            "peso_torax": (
                peso_torax
            ),

            "peso_ombros": (
                peso_ombros
            ),

            "largura_base_cm": round(
                largura_base,
                2,
            ),

            "fator_corporal": (
                fator_corporal
            ),

            "fator_modelagem": (
                fator_modelagem
            ),
        },

        "relacao_corporal": (
            relacao_corporal
        ),

        "modelagem": (
            modelagem_normalizada
        ),

        "plausibilidade": {
            "plausivel": (
                plausivel
            ),

            "faixa_min_cm": 20.0,
            "faixa_max_cm": 70.0,
        },

        "confianca": (
            confianca
        ),

        "natureza": (
            "metrica_horizontal_derivada_para_vestuario"
        ),

        "origem": (
            "composicao_torax_ombros_geometria_2d"
        ),

        "experimental": True,

        "equivalencia_antropometrica_exata": (
            False
        ),

        "uso_direto_em_roupa": (
            False
        ),

        "uso_para_comparacao_dimensional": (
            disponivel
        ),

        "uso_para_recomendacao_tamanho": (
            False
        ),

        "mensagem": (
            "Largura corporal equivalente experimental "
            "calculada a partir de métricas visuais do "
            "tórax e dos ombros. O valor serve como "
            "referência horizontal interna do VesteIA "
            "e ainda não representa uma medida "
            "antropométrica exata."
        ),
    }