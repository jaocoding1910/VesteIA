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
        str(
            preferencia_caimento
        )
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

    modelagem_normalizada = (
        str(
            modelagem
        )
        .strip()
        .lower()
    )

    mapa = {
        "slim": "slim",
        "slim fit": "slim",
        "ajustada": "slim",
        "ajustado": "slim",

        "regular": "regular",
        "padrao": "regular",
        "padrão": "regular",
        "normal": "regular",
        "reta": "regular",

        "oversized": "oversized",
        "over": "oversized",
        "ampla": "oversized",
        "amplo": "oversized",
        "solta": "oversized",
        "solto": "oversized",
    }

    return mapa.get(
        modelagem_normalizada,
        "regular",
    )


def _obter_alvos_preferencia(
    preferencia_caimento,
    modelagem=None,
):
    """
    Define os alvos experimentais
    utilizados pelo motor de tamanho.

    O alvo dimensional considera:

    1. preferência do usuário;
    2. modelagem real da peça.
    """

    preferencia = (
        _normalizar_preferencia_caimento(
            preferencia_caimento
        )
    )

    modelagem_normalizada = (
        _normalizar_modelagem(
            modelagem
        )
    )

    configuracoes_preferencia = {
        "justo": {
            "indice_largura_alvo": 1.04,
            "indice_comprimento_alvo": 1.17,
            "peso_largura": 0.65,
            "peso_comprimento": 0.35,
        },

        "padrao": {
            "indice_largura_alvo": 1.10,
            "indice_comprimento_alvo": 1.22,
            "peso_largura": 0.65,
            "peso_comprimento": 0.35,
        },

        "solto": {
            "indice_largura_alvo": 1.18,
            "indice_comprimento_alvo": 1.27,
            "peso_largura": 0.70,
            "peso_comprimento": 0.30,
        },
    }

    configuracao = dict(
        configuracoes_preferencia[
            preferencia
        ]
    )

    ajustes_modelagem = {
        "slim": {
            "fator_largura": 0.94,
            "fator_comprimento": 0.98,
        },

        "regular": {
            "fator_largura": 1.00,
            "fator_comprimento": 1.00,
        },

        "oversized": {
            "fator_largura": 1.52,
            "fator_comprimento": 1.04,
        },
    }

    ajuste = (
        ajustes_modelagem[
            modelagem_normalizada
        ]
    )

    configuracao[
        "indice_largura_alvo"
    ] = round(
        configuracao[
            "indice_largura_alvo"
        ]
        * ajuste[
            "fator_largura"
        ],
        4,
    )

    configuracao[
        "indice_comprimento_alvo"
    ] = round(
        configuracao[
            "indice_comprimento_alvo"
        ]
        * ajuste[
            "fator_comprimento"
        ],
        4,
    )

    return {
        "preferencia": preferencia,
        "modelagem": modelagem_normalizada,
        "fator_modelagem_largura": (
            ajuste["fator_largura"]
        ),
        "fator_modelagem_comprimento": (
            ajuste["fator_comprimento"]
        ),
        **configuracao,
    }


def _valor_numerico(
    valor,
):
    if valor is None:
        return None

    try:
        valor = float(
            valor
        )
    except (
        TypeError,
        ValueError,
    ):
        return None

    if valor <= 0:
        return None

    return valor


def _calcular_score(
    indice,
    alvo,
    tolerancia,
):
    if indice is None:
        return None

    diferenca = abs(
        indice
        - alvo
    )

    score = (
        1
        - (
            diferenca
            / tolerancia
        )
    )

    score = max(
        0,
        min(
            score,
            1,
        ),
    )

    return round(
        score,
        4,
    )


def _classificar_largura(
    indice_largura,
    alvo_largura=None,
):
    if indice_largura is None:
        return "indisponivel"

    if alvo_largura is None:
        if indice_largura < 1.03:
            return "ajustado"

        if indice_largura < 1.15:
            return "equilibrado"

        return "amplo"

    proporcao_alvo = (
        indice_largura
        / alvo_largura
    )

    if proporcao_alvo < 0.94:
        return "mais_ajustado_que_alvo"

    if proporcao_alvo <= 1.06:
        return "equilibrado"

    return "mais_amplo_que_alvo"


def _classificar_comprimento(
    indice_comprimento,
    alvo_comprimento=None,
):
    if indice_comprimento is None:
        return "indisponivel"

    if alvo_comprimento is None:
        if indice_comprimento < 1.12:
            return "curto"

        if indice_comprimento < 1.20:
            return "equilibrado"

        return "alongado"

    proporcao_alvo = (
        indice_comprimento
        / alvo_comprimento
    )

    if proporcao_alvo < 0.95:
        return "mais_curto_que_alvo"

    if proporcao_alvo <= 1.05:
        return "equilibrado"

    return "mais_alongado_que_alvo"


def _obter_metricas_vestuario(
    deteccao,
):
    metricas = (
        deteccao.get(
            "metricas_corporais_vestuario"
        )
        or {}
    )

    medidas = (
        metricas.get(
            "medidas"
        )
        or {}
    )

    comparacao_direta = set(
        metricas.get(
            "metricas_para_comparacao_direta",
            [],
        )
        or []
    )

    apenas_visuais = set(
        metricas.get(
            "metricas_apenas_visuais",
            [],
        )
        or []
    )

    return {
        "status": metricas.get(
            "status"
        ),
        "metricas_liberadas": metricas.get(
            "metricas_liberadas",
            False,
        ),
        "medidas": medidas,
        "comparacao_direta": comparacao_direta,
        "apenas_visuais": apenas_visuais,
    }


def _obter_medida_cm(
    medidas,
    nome,
):
    metrica = (
        medidas.get(
            nome
        )
        or {}
    )

    return (
        _valor_numerico(
            metrica.get(
                "valor_cm"
            )
        )
    )


def _obter_calibracao_vestuario(
    deteccao,
):
    calibracao = (
        deteccao.get(
            "calibracao_vestuario"
        )
        or {}
    )

    largura = (
        _valor_numerico(
            calibracao.get(
                "largura_corporal_vestuario_cm"
            )
        )
    )

    comprimento = (
        _valor_numerico(
            calibracao.get(
                "comprimento_corporal_vestuario_cm"
            )
        )
    )

    horizontal_liberada = bool(
        calibracao.get(
            "comparacao_horizontal_disponivel",
            False,
        )
    )

    vertical_liberada = bool(
        calibracao.get(
            "comparacao_vertical_disponivel",
            False,
        )
    )

    qualidade = (
        calibracao.get(
            "qualidade"
        )
        or {}
    )

    qualidade_nivel = (
        qualidade.get(
            "nivel"
        )
    )

    qualidade_pontuacao = (
        _valor_numerico(
            qualidade.get(
                "pontuacao"
            )
        )
    )

    largura_disponivel = (
        horizontal_liberada
        and largura is not None
    )

    comprimento_disponivel = (
        vertical_liberada
        and comprimento is not None
    )

    return {
        "status": calibracao.get(
            "status"
        ),
        "calibracao_disponivel": calibracao.get(
            "calibracao_disponivel",
            False,
        ),
        "largura_corporal_vestuario_cm": largura,
        "comprimento_corporal_vestuario_cm": comprimento,
        "comparacao_horizontal_disponivel": largura_disponivel,
        "comparacao_vertical_disponivel": comprimento_disponivel,
        "qualidade": {
            "nivel": qualidade_nivel,
            "pontuacao": qualidade_pontuacao,
        },
        "experimental": calibracao.get(
            "experimental",
            True,
        ),
        "versao": calibracao.get(
            "versao_calibracao"
        ),
        "modelagem": calibracao.get(
            "modelagem"
        ),
        "preferencia_caimento": calibracao.get(
            "preferencia_caimento"
        ),
    }


def _obter_referencias_dimensionais(
    deteccao,
):
    calibracao = (
        _obter_calibracao_vestuario(
            deteccao
        )
    )

    contrato = (
        _obter_metricas_vestuario(
            deteccao
        )
    )

    medidas_semanticas = (
        contrato.get(
            "medidas",
            {},
        )
    )

    comparacao_direta = (
        contrato.get(
            "comparacao_direta",
            set(),
        )
    )

    largura_cm = None
    origem_largura = None

    if calibracao.get(
        "comparacao_horizontal_disponivel"
    ):
        largura_cm = calibracao.get(
            "largura_corporal_vestuario_cm"
        )
        origem_largura = (
            "calibracao_vestuario"
        )

    if largura_cm is None:
        largura_equivalente = (
            deteccao.get(
                "largura_corporal_equivalente"
            )
            or {}
        )

        if largura_equivalente.get(
            "disponivel",
            False,
        ):
            largura_cm = (
                _valor_numerico(
                    largura_equivalente.get(
                        "largura_corporal_equivalente_cm"
                    )
                )
            )

            if largura_cm is not None:
                origem_largura = (
                    "largura_corporal_equivalente"
                )

    comprimento_cm = None
    origem_comprimento = None

    if calibracao.get(
        "comparacao_vertical_disponivel"
    ):
        comprimento_cm = calibracao.get(
            "comprimento_corporal_vestuario_cm"
        )
        origem_comprimento = (
            "calibracao_vestuario"
        )

    if comprimento_cm is None:
        if "tronco" in comparacao_direta:
            comprimento_cm = (
                _obter_medida_cm(
                    medidas_semanticas,
                    "tronco",
                )
            )

            if comprimento_cm is not None:
                origem_comprimento = (
                    "metricas_corporais_vestuario.tronco"
                )

    return {
        "largura_cm": largura_cm,
        "comprimento_cm": comprimento_cm,
        "largura_disponivel": (
            largura_cm is not None
        ),
        "comprimento_disponivel": (
            comprimento_cm is not None
        ),
        "origem_largura": origem_largura,
        "origem_comprimento": origem_comprimento,
        "calibracao_vestuario": calibracao,
        "metricas_apenas_visuais": contrato.get(
            "apenas_visuais",
            set(),
        ),
    }


def _resultado_ranking_parcial(
    posicao,
    largura_disponivel,
    comprimento_disponivel,
):
    if (
        comprimento_disponivel
        and not largura_disponivel
    ):
        if posicao == 1:
            return "melhor_compatibilidade_vertical"

        return "alternativa_vertical"

    if (
        largura_disponivel
        and not comprimento_disponivel
    ):
        if posicao == 1:
            return "melhor_compatibilidade_horizontal"

        return "alternativa_horizontal"

    if posicao == 1:
        return "melhor_compatibilidade_parcial"

    return "alternativa_parcial"


def _resultado_ranking_completo(
    posicao,
    caimento_largura,
):
    if posicao == 1:
        return "melhor_equilibrio"

    if caimento_largura == "mais_amplo_que_alvo":
        return "alternativa_mais_ampla"

    if caimento_largura == "mais_ajustado_que_alvo":
        return "alternativa_mais_ajustada"

    return "alternativa"


def _calcular_confianca_ranking(
    ranking,
    ranking_parcial=True,
):
    if not ranking:
        return {
            "nivel": "indisponivel",
            "nivel_matematico": "indisponivel",
            "diferenca_primeiro_segundo": None,
            "primeiro_colocado": None,
            "segundo_colocado": None,
            "pontuacao_primeiro": None,
            "pontuacao_segundo": None,
            "ranking_parcial": ranking_parcial,
            "observacao": (
                "Não existem opções suficientes "
                "para calcular a confiança."
            ),
        }

    primeiro = ranking[0]

    if len(ranking) == 1:
        return {
            "nivel": "baixa",
            "nivel_matematico": "baixa",
            "diferenca_primeiro_segundo": None,
            "primeiro_colocado": primeiro.get(
                "tamanho"
            ),
            "segundo_colocado": None,
            "pontuacao_primeiro": primeiro.get(
                "pontuacao"
            ),
            "pontuacao_segundo": None,
            "ranking_parcial": ranking_parcial,
            "observacao": (
                "Existe apenas uma opção "
                "válida para comparação."
            ),
        }

    segundo = ranking[1]

    pontuacao_primeiro = float(
        primeiro.get(
            "pontuacao",
            0,
        )
        or 0
    )

    pontuacao_segundo = float(
        segundo.get(
            "pontuacao",
            0,
        )
        or 0
    )

    diferenca = round(
        max(
            pontuacao_primeiro
            - pontuacao_segundo,
            0,
        ),
        4,
    )

    if diferenca >= 0.10:
        nivel_base = "alta"

    elif diferenca >= 0.04:
        nivel_base = "media"

    else:
        nivel_base = "baixa"

    if ranking_parcial:
        if nivel_base == "alta":
            nivel = "media"
        else:
            nivel = "baixa"

        observacao = (
            "A separação matemática entre "
            "os tamanhos foi calculada com "
            "apenas parte das dimensões "
            "necessárias."
        )

    else:
        nivel = nivel_base

        if nivel == "alta":
            observacao = (
                "O primeiro tamanho apresentou "
                "vantagem clara sobre a "
                "segunda opção no ranking "
                "experimental."
            )

        elif nivel == "media":
            observacao = (
                "O primeiro tamanho apresentou "
                "vantagem moderada sobre a "
                "segunda opção no ranking "
                "experimental."
            )

        else:
            observacao = (
                "Os dois melhores tamanhos "
                "ficaram muito próximos no "
                "ranking experimental."
            )

    return {
        "nivel": nivel,
        "nivel_matematico": nivel_base,
        "diferenca_primeiro_segundo": diferenca,
        "primeiro_colocado": primeiro.get(
            "tamanho"
        ),
        "segundo_colocado": segundo.get(
            "tamanho"
        ),
        "pontuacao_primeiro": round(
            pontuacao_primeiro,
            4,
        ),
        "pontuacao_segundo": round(
            pontuacao_segundo,
            4,
        ),
        "ranking_parcial": ranking_parcial,
        "observacao": observacao,
    }


def _avaliar_zona_decisao_ranking(
    ranking,
    ranking_parcial=False,
):
    """
    Faixas experimentais:

    diferença < 0.04
        empate técnico

    0.04 <= diferença < 0.10
        vantagem moderada

    diferença >= 0.10
        vantagem clara
    """

    if not ranking:
        return {
            "status": "indisponivel",
            "empate_tecnico": False,
            "diferenca": None,
            "limiar_empate_tecnico": 0.04,
            "limiar_vantagem_clara": 0.10,
            "primeiro": None,
            "segundo": None,
            "pontuacao_primeiro": None,
            "pontuacao_segundo": None,
            "ranking_parcial": ranking_parcial,
            "mensagem": (
                "Não existem opções suficientes "
                "para avaliar a zona de decisão."
            ),
        }

    primeiro = ranking[0]

    if len(ranking) < 2:
        return {
            "status": "opcao_unica",
            "empate_tecnico": False,
            "diferenca": None,
            "limiar_empate_tecnico": 0.04,
            "limiar_vantagem_clara": 0.10,
            "primeiro": primeiro.get(
                "tamanho"
            ),
            "segundo": None,
            "pontuacao_primeiro": primeiro.get(
                "pontuacao"
            ),
            "pontuacao_segundo": None,
            "ranking_parcial": ranking_parcial,
            "mensagem": (
                "Existe apenas uma opção válida "
                "para comparação."
            ),
        }

    segundo = ranking[1]

    pontuacao_primeiro = float(
        primeiro.get(
            "pontuacao",
            0,
        )
        or 0
    )

    pontuacao_segundo = float(
        segundo.get(
            "pontuacao",
            0,
        )
        or 0
    )

    diferenca = round(
        max(
            pontuacao_primeiro
            - pontuacao_segundo,
            0,
        ),
        4,
    )

    if diferenca < 0.04:
        status = "empate_tecnico"
        empate_tecnico = True

        mensagem = (
            f"Os tamanhos "
            f"{primeiro.get('tamanho')} e "
            f"{segundo.get('tamanho')} "
            "apresentaram resultados muito "
            "próximos no ranking experimental."
        )

    elif diferenca < 0.10:
        status = "vantagem_moderada"
        empate_tecnico = False

        mensagem = (
            f"O tamanho "
            f"{primeiro.get('tamanho')} "
            "apresentou vantagem moderada "
            f"sobre {segundo.get('tamanho')}."
        )

    else:
        status = "vantagem_clara"
        empate_tecnico = False

        mensagem = (
            f"O tamanho "
            f"{primeiro.get('tamanho')} "
            "apresentou vantagem clara "
            f"sobre {segundo.get('tamanho')}."
        )

    if ranking_parcial:
        mensagem += (
            " A comparação utiliza apenas "
            "parte das dimensões necessárias."
        )

    return {
        "status": status,
        "empate_tecnico": empate_tecnico,
        "diferenca": diferenca,
        "limiar_empate_tecnico": 0.04,
        "limiar_vantagem_clara": 0.10,
        "primeiro": primeiro.get(
            "tamanho"
        ),
        "segundo": segundo.get(
            "tamanho"
        ),
        "pontuacao_primeiro": round(
            pontuacao_primeiro,
            4,
        ),
        "pontuacao_segundo": round(
            pontuacao_segundo,
            4,
        ),
        "ranking_parcial": ranking_parcial,
        "mensagem": mensagem,
    }


def _gerar_explicacao_decisao_parcial(
    melhor,
    segundo,
    preferencia,
    largura_disponivel,
    comprimento_disponivel,
):
    if not melhor:
        return {
            "motivo_principal": "indisponivel",
            "preferencia_caimento": preferencia,
            "ranking_parcial": True,
            "mensagem": (
                "Não foi possível gerar "
                "uma análise dimensional."
            ),
        }

    tamanho = melhor.get(
        "tamanho"
    )

    if (
        comprimento_disponivel
        and not largura_disponivel
    ):
        motivo = (
            "comprimento_mais_proximo_do_alvo"
        )

        mensagem = (
            f"O tamanho {tamanho} apresentou "
            "a relação vertical mais próxima "
            "do alvo experimental."
        )

    elif (
        largura_disponivel
        and not comprimento_disponivel
    ):
        motivo = (
            "largura_mais_proxima_do_alvo"
        )

        mensagem = (
            f"O tamanho {tamanho} apresentou "
            "a relação horizontal mais próxima "
            "do alvo experimental."
        )

    else:
        motivo = (
            "comparacao_dimensional_parcial"
        )

        mensagem = (
            f"O tamanho {tamanho} apresentou "
            "o melhor resultado entre as "
            "dimensões disponíveis."
        )

    if segundo:
        primeiro_score = float(
            melhor.get(
                "pontuacao",
                0,
            )
            or 0
        )

        segundo_score = float(
            segundo.get(
                "pontuacao",
                0,
            )
            or 0
        )

        diferenca = abs(
            primeiro_score
            - segundo_score
        )

        if diferenca < 0.04:
            mensagem += (
                f" O tamanho "
                f"{segundo.get('tamanho')} "
                "também ficou muito próximo."
            )

    return {
        "motivo_principal": motivo,
        "largura": melhor.get(
            "caimento_largura"
        ),
        "comprimento": melhor.get(
            "caimento_comprimento"
        ),
        "score_largura": melhor.get(
            "score_largura"
        ),
        "score_comprimento": melhor.get(
            "score_comprimento"
        ),
        "preferencia_caimento": preferencia,
        "ranking_parcial": True,
        "mensagem": mensagem,
    }


def _gerar_explicacao_decisao_completa(
    melhor,
    segundo,
    preferencia,
):
    if not melhor:
        return {
            "motivo_principal": "indisponivel",
            "preferencia_caimento": preferencia,
            "ranking_parcial": False,
            "mensagem": (
                "Não foi possível explicar "
                "a análise de tamanho."
            ),
        }

    score_largura = float(
        melhor.get(
            "score_largura",
            0,
        )
        or 0
    )

    score_comprimento = float(
        melhor.get(
            "score_comprimento",
            0,
        )
        or 0
    )

    if abs(
        score_largura
        - score_comprimento
    ) <= 0.08:
        motivo_principal = (
            "melhor_equilibrio_largura_comprimento"
        )

    elif score_largura > score_comprimento:
        motivo_principal = (
            "largura_mais_proxima_do_alvo"
        )

    else:
        motivo_principal = (
            "comprimento_mais_proximo_do_alvo"
        )

    mensagens_preferencia = {
        "justo": (
            "priorizando um caimento "
            "mais ajustado"
        ),
        "padrao": (
            "buscando equilíbrio entre "
            "ajuste e conforto"
        ),
        "solto": (
            "priorizando um caimento "
            "mais solto"
        ),
    }

    mensagem = (
        f"O tamanho {melhor.get('tamanho')} "
        "obteve o melhor equilíbrio entre "
        "a referência horizontal e vertical, "
        f"{mensagens_preferencia[preferencia]}."
    )

    if segundo:
        primeiro_score = float(
            melhor.get(
                "pontuacao",
                0,
            )
            or 0
        )

        segundo_score = float(
            segundo.get(
                "pontuacao",
                0,
            )
            or 0
        )

        diferenca = abs(
            primeiro_score
            - segundo_score
        )

        if diferenca < 0.04:
            mensagem += (
                f" O tamanho "
                f"{segundo.get('tamanho')} "
                "ficou muito próximo e também "
                "pode ser considerado como "
                "alternativa experimental."
            )

        elif diferenca < 0.10:
            mensagem += (
                f" O tamanho "
                f"{segundo.get('tamanho')} "
                "permanece como alternativa "
                "relevante devido à margem "
                "moderada entre os resultados."
            )

    return {
        "motivo_principal": motivo_principal,
        "largura": melhor.get(
            "caimento_largura"
        ),
        "comprimento": melhor.get(
            "caimento_comprimento"
        ),
        "score_largura": round(
            score_largura,
            4,
        ),
        "score_comprimento": round(
            score_comprimento,
            4,
        ),
        "preferencia_caimento": preferencia,
        "ranking_parcial": False,
        "mensagem": mensagem,
    }


def _retorno_indisponivel(
    status,
    preferencia,
    mensagem,
    mensagem_transparencia,
):
    return {
        "status": status,
        "disponivel": False,
        "tamanho": None,
        "tamanho_sugerido": None,
        "tamanho_alternativo": None,
        "empate_tecnico": False,
        "alternativa_forte": False,
        "decisao_unica": False,
        "preferencia_caimento": preferencia,
        "pontuacao": None,
        "pontuacao_melhor_tamanho": None,
        "ranking": [],
        "ranking_parcial": False,
        "dimensoes_utilizadas": [],
        "dimensoes_pendentes": [],
        "metrica_horizontal_utilizada": None,
        "metrica_vertical_utilizada": None,
        "confianca_ranking": {
            "nivel": "indisponivel",
            "diferenca_primeiro_segundo": None,
        },
        "zona_decisao": {
            "status": "indisponivel",
            "empate_tecnico": False,
            "diferenca": None,
        },
        "explicacao_decisao": None,
        "nivel": "indisponivel",
        "recomendacao_definitiva": False,
        "sugestao_experimental": False,
        "mensagem": mensagem,
        "mensagem_transparencia": (
            mensagem_transparencia
        ),
    }


def gerar_recomendacao_tamanho_provador(
    variacoes_produto,
    deteccao,
    preferencia_caimento="padrao",
):
    """
    Motor dimensional de comparação
    entre tamanhos do VesteIA.

    Sprint 48 V1:
    - modelagem aplicada aos alvos;
    - preferência de caimento;
    - empate técnico;
    - vantagem moderada com alternativa forte;
    - vantagem clara com decisão isolada;
    - ranking experimental.
    """

    preferencia = (
        _normalizar_preferencia_caimento(
            preferencia_caimento
        )
    )

    if not variacoes_produto:
        return (
            _retorno_indisponivel(
                status="variacoes_indisponiveis",
                preferencia=preferencia,
                mensagem=(
                    "Não existem variações "
                    "suficientes para comparar "
                    "os tamanhos."
                ),
                mensagem_transparencia=(
                    "Não foi possível calcular "
                    "uma análise dimensional."
                ),
            )
        )

    if not deteccao:
        return (
            _retorno_indisponivel(
                status="deteccao_indisponivel",
                preferencia=preferencia,
                mensagem=(
                    "Os dados corporais não "
                    "estão disponíveis."
                ),
                mensagem_transparencia=(
                    "O VesteIA precisa concluir "
                    "a análise corporal antes "
                    "de avaliar os tamanhos."
                ),
            )
        )

    referencias = (
        _obter_referencias_dimensionais(
            deteccao
        )
    )

    largura_corporal_cm = (
        referencias.get(
            "largura_cm"
        )
    )

    comprimento_corporal_cm = (
        referencias.get(
            "comprimento_cm"
        )
    )

    largura_disponivel = (
        referencias.get(
            "largura_disponivel",
            False,
        )
    )

    comprimento_disponivel = (
        referencias.get(
            "comprimento_disponivel",
            False,
        )
    )

    origem_largura = (
        referencias.get(
            "origem_largura"
        )
    )

    origem_comprimento = (
        referencias.get(
            "origem_comprimento"
        )
    )

    calibracao_vestuario = (
        referencias.get(
            "calibracao_vestuario",
            {},
        )
    )

    apenas_visuais = (
        referencias.get(
            "metricas_apenas_visuais",
            set(),
        )
    )

    if (
        not largura_disponivel
        and not comprimento_disponivel
    ):
        retorno = (
            _retorno_indisponivel(
                status=(
                    "dimensoes_comparaveis_indisponiveis"
                ),
                preferencia=preferencia,
                mensagem=(
                    "Ainda não existem referências "
                    "corporais de vestuário suficientes "
                    "para comparar os tamanhos."
                ),
                mensagem_transparencia=(
                    "O VesteIA não utiliza projeções "
                    "visuais isoladas como equivalentes "
                    "diretos às medidas cadastradas "
                    "da roupa."
                ),
            )
        )

        retorno[
            "metricas_apenas_visuais"
        ] = sorted(
            apenas_visuais
        )

        return retorno

    modelagem = (
        calibracao_vestuario.get(
            "modelagem"
        )
    )

    if not modelagem:
        for variacao in variacoes_produto:
            modelagem_variacao = (
                variacao.get(
                    "modelagem"
                )
            )

            if modelagem_variacao:
                modelagem = (
                    modelagem_variacao
                )
                break

    modelagem_normalizada = (
        _normalizar_modelagem(
            modelagem
        )
    )

    configuracao = (
        _obter_alvos_preferencia(
            preferencia_caimento=preferencia,
            modelagem=modelagem_normalizada,
        )
    )

    indice_largura_alvo = (
        configuracao[
            "indice_largura_alvo"
        ]
    )

    indice_comprimento_alvo = (
        configuracao[
            "indice_comprimento_alvo"
        ]
    )

    peso_largura_original = (
        configuracao[
            "peso_largura"
        ]
    )

    peso_comprimento_original = (
        configuracao[
            "peso_comprimento"
        ]
    )

    dimensoes_utilizadas = []
    dimensoes_pendentes = []

    if largura_disponivel:
        dimensoes_utilizadas.append(
            "largura"
        )
    else:
        dimensoes_pendentes.append(
            "largura"
        )

    if comprimento_disponivel:
        dimensoes_utilizadas.append(
            "comprimento"
        )
    else:
        dimensoes_pendentes.append(
            "comprimento"
        )

    ranking_parcial = bool(
        dimensoes_pendentes
    )

    if (
        largura_disponivel
        and comprimento_disponivel
    ):
        peso_largura_efetivo = (
            peso_largura_original
        )
        peso_comprimento_efetivo = (
            peso_comprimento_original
        )

    elif largura_disponivel:
        peso_largura_efetivo = 1.0
        peso_comprimento_efetivo = 0.0

    else:
        peso_largura_efetivo = 0.0
        peso_comprimento_efetivo = 1.0

    ranking = []

    for produto in variacoes_produto:
        largura_peca_cm = (
            _valor_numerico(
                produto.get(
                    "largura_cm"
                )
            )
        )

        comprimento_peca_cm = (
            _valor_numerico(
                produto.get(
                    "comprimento_cm"
                )
            )
        )

        indice_largura = None
        score_largura = None
        caimento_largura = "indisponivel"

        indice_comprimento = None
        score_comprimento = None
        caimento_comprimento = "indisponivel"

        if (
            largura_disponivel
            and largura_peca_cm is not None
        ):
            indice_largura = (
                largura_peca_cm
                / largura_corporal_cm
            )

            score_largura = (
                _calcular_score(
                    indice=indice_largura,
                    alvo=indice_largura_alvo,
                    tolerancia=0.42,
                )
            )

            caimento_largura = (
                _classificar_largura(
                    indice_largura=indice_largura,
                    alvo_largura=indice_largura_alvo,
                )
            )

        if (
            comprimento_disponivel
            and comprimento_peca_cm is not None
        ):
            indice_comprimento = (
                comprimento_peca_cm
                / comprimento_corporal_cm
            )

            score_comprimento = (
                _calcular_score(
                    indice=indice_comprimento,
                    alvo=indice_comprimento_alvo,
                    tolerancia=0.35,
                )
            )

            caimento_comprimento = (
                _classificar_comprimento(
                    indice_comprimento=indice_comprimento,
                    alvo_comprimento=indice_comprimento_alvo,
                )
            )

        componentes = []

        if score_largura is not None:
            componentes.append(
                (
                    score_largura,
                    peso_largura_efetivo,
                )
            )

        if score_comprimento is not None:
            componentes.append(
                (
                    score_comprimento,
                    peso_comprimento_efetivo,
                )
            )

        if not componentes:
            continue

        soma_pesos = sum(
            peso
            for _, peso
            in componentes
        )

        if soma_pesos <= 0:
            continue

        pontuacao = (
            sum(
                score * peso
                for score, peso
                in componentes
            )
            / soma_pesos
        )

        ranking.append(
            {
                "produto_id": produto.get(
                    "id"
                ),
                "tamanho": produto.get(
                    "tamanho"
                ),
                "largura_peca_cm": (
                    round(
                        largura_peca_cm,
                        2,
                    )
                    if largura_peca_cm is not None
                    else None
                ),
                "comprimento_peca_cm": (
                    round(
                        comprimento_peca_cm,
                        2,
                    )
                    if comprimento_peca_cm is not None
                    else None
                ),
                "indice_largura": (
                    round(
                        indice_largura,
                        4,
                    )
                    if indice_largura is not None
                    else None
                ),
                "indice_comprimento": (
                    round(
                        indice_comprimento,
                        4,
                    )
                    if indice_comprimento is not None
                    else None
                ),
                "caimento_largura": (
                    caimento_largura
                ),
                "caimento_comprimento": (
                    caimento_comprimento
                ),
                "score_largura": (
                    score_largura
                ),
                "score_comprimento": (
                    score_comprimento
                ),
                "pontuacao": round(
                    pontuacao,
                    4,
                ),
                "ranking_parcial": (
                    ranking_parcial
                ),
                "dimensoes_utilizadas": list(
                    dimensoes_utilizadas
                ),
                "origem_referencia_horizontal": (
                    origem_largura
                ),
                "origem_referencia_vertical": (
                    origem_comprimento
                ),
                "modelagem_avaliada": (
                    modelagem_normalizada
                ),
            }
        )

    if not ranking:
        retorno = (
            _retorno_indisponivel(
                status=(
                    "variacoes_sem_medidas_comparaveis"
                ),
                preferencia=preferencia,
                mensagem=(
                    "As variações não possuem "
                    "medidas suficientes para "
                    "a comparação dimensional."
                ),
                mensagem_transparencia=(
                    "Nenhum tamanho pôde ser "
                    "avaliado com as referências "
                    "corporais disponíveis."
                ),
            )
        )

        retorno[
            "dimensoes_pendentes"
        ] = dimensoes_pendentes

        return retorno

    ranking.sort(
        key=lambda item: (
            item.get(
                "pontuacao",
                0,
            )
        ),
        reverse=True,
    )

    for indice, item in enumerate(
        ranking,
        start=1,
    ):
        item["posicao"] = indice

        if ranking_parcial:
            item[
                "resultado"
            ] = (
                _resultado_ranking_parcial(
                    posicao=indice,
                    largura_disponivel=largura_disponivel,
                    comprimento_disponivel=comprimento_disponivel,
                )
            )

        else:
            item[
                "resultado"
            ] = (
                _resultado_ranking_completo(
                    posicao=indice,
                    caimento_largura=item.get(
                        "caimento_largura"
                    ),
                )
            )

    melhor = ranking[0]

    segundo = (
        ranking[1]
        if len(ranking) > 1
        else None
    )

    confianca_ranking = (
        _calcular_confianca_ranking(
            ranking=ranking,
            ranking_parcial=ranking_parcial,
        )
    )

    zona_decisao = (
        _avaliar_zona_decisao_ranking(
            ranking=ranking,
            ranking_parcial=ranking_parcial,
        )
    )

    if ranking_parcial:
        explicacao_decisao = (
            _gerar_explicacao_decisao_parcial(
                melhor=melhor,
                segundo=segundo,
                preferencia=preferencia,
                largura_disponivel=largura_disponivel,
                comprimento_disponivel=comprimento_disponivel,
            )
        )

        return {
            "status": (
                "ranking_dimensional_parcial"
            ),
            "disponivel": False,
            "tamanho": None,
            "tamanho_sugerido": None,
            "tamanho_alternativo": None,
            "empate_tecnico": zona_decisao.get(
                "empate_tecnico",
                False,
            ),
            "alternativa_forte": False,
            "decisao_unica": False,
            "preferencia_caimento": preferencia,
            "modelagem": modelagem_normalizada,
            "ranking_parcial": True,
            "dimensoes_utilizadas": (
                dimensoes_utilizadas
            ),
            "dimensoes_pendentes": (
                dimensoes_pendentes
            ),
            "metricas_apenas_visuais": sorted(
                apenas_visuais
            ),
            "metrica_horizontal_utilizada": (
                origem_largura
            ),
            "metrica_vertical_utilizada": (
                origem_comprimento
            ),
            "alvos_utilizados": {
                "indice_largura": (
                    indice_largura_alvo
                    if largura_disponivel
                    else None
                ),
                "indice_comprimento": (
                    indice_comprimento_alvo
                    if comprimento_disponivel
                    else None
                ),
                "peso_largura_original": (
                    peso_largura_original
                ),
                "peso_comprimento_original": (
                    peso_comprimento_original
                ),
                "peso_largura_efetivo": (
                    peso_largura_efetivo
                ),
                "peso_comprimento_efetivo": (
                    peso_comprimento_efetivo
                ),
                "modelagem": (
                    modelagem_normalizada
                ),
                "fator_modelagem_largura": (
                    configuracao.get(
                        "fator_modelagem_largura"
                    )
                ),
                "fator_modelagem_comprimento": (
                    configuracao.get(
                        "fator_modelagem_comprimento"
                    )
                ),
            },
            "medidas_corporais_referencia": {
                "largura_corporal_vestuario_cm": (
                    round(
                        largura_corporal_cm,
                        2,
                    )
                    if largura_corporal_cm is not None
                    else None
                ),
                "comprimento_corporal_vestuario_cm": (
                    round(
                        comprimento_corporal_cm,
                        2,
                    )
                    if comprimento_corporal_cm is not None
                    else None
                ),
                "origem_horizontal": (
                    origem_largura
                ),
                "origem_vertical": (
                    origem_comprimento
                ),
            },
            "pontuacao": melhor.get(
                "pontuacao"
            ),
            "pontuacao_melhor_tamanho": (
                melhor.get(
                    "pontuacao"
                )
            ),
            "ranking": ranking,
            "confianca_ranking": (
                confianca_ranking
            ),
            "zona_decisao": (
                zona_decisao
            ),
            "explicacao_decisao": (
                explicacao_decisao
            ),
            "nivel": (
                "experimental_parcial"
            ),
            "recomendacao_definitiva": False,
            "sugestao_experimental": False,
            "mensagem": (
                "O VesteIA conseguiu comparar "
                "parcialmente os tamanhos."
            ),
            "mensagem_transparencia": (
                "O primeiro colocado do ranking "
                "parcial não representa uma "
                "recomendação final."
            ),
        }

    tamanho_sugerido = (
        melhor.get(
            "tamanho"
        )
    )

    explicacao_decisao = (
        _gerar_explicacao_decisao_completa(
            melhor=melhor,
            segundo=segundo,
            preferencia=preferencia,
        )
    )

    mensagens_preferencia = {
        "justo": (
            "considerando sua preferência "
            "por um caimento mais ajustado"
        ),
        "padrao": (
            "considerando um equilíbrio "
            "entre ajuste e conforto"
        ),
        "solto": (
            "considerando sua preferência "
            "por um caimento mais solto"
        ),
    }

    # =====================================================
    # ZONA FINAL DE DECISÃO
    # =====================================================

    status_zona_decisao = (
        zona_decisao.get(
            "status",
            "indisponivel",
        )
    )

    empate_tecnico = (
        status_zona_decisao
        == "empate_tecnico"
    )

    vantagem_moderada = (
        status_zona_decisao
        == "vantagem_moderada"
    )

    vantagem_clara = (
        status_zona_decisao
        == "vantagem_clara"
    )

    alternativa_forte = (
        empate_tecnico
        or vantagem_moderada
    )

    tamanho_alternativo = (
        segundo.get(
            "tamanho"
        )
        if (
            alternativa_forte
            and segundo
        )
        else None
    )

    decisao_unica = (
        vantagem_clara
    )

    # =====================================================
    # MENSAGEM FINAL
    # =====================================================

    if empate_tecnico:
        mensagem_final = (
            f"Os tamanhos {tamanho_sugerido} e "
            f"{tamanho_alternativo} apresentaram "
            "resultados muito próximos. "
            f"O tamanho {tamanho_sugerido} obteve "
            "a maior pontuação experimental, "
            f"mas {tamanho_alternativo} também "
            "permanece como uma opção compatível "
            "com a preferência de caimento."
        )

    elif vantagem_moderada:
        mensagem_final = (
            f"O tamanho {tamanho_sugerido} apresentou "
            "a melhor pontuação experimental, mas "
            f"{tamanho_alternativo} permanece como "
            "uma alternativa relevante devido à "
            "margem moderada entre os dois tamanhos. "
            f"A análise considera a modelagem "
            f"{modelagem_normalizada} e "
            f"{mensagens_preferencia[preferencia]}."
        )

    else:
        mensagem_final = (
            f"O tamanho {tamanho_sugerido} "
            "apresentou vantagem clara no equilíbrio "
            "experimental entre largura e comprimento, "
            f"considerando a modelagem "
            f"{modelagem_normalizada} e "
            f"{mensagens_preferencia[preferencia]}."
        )

    if empate_tecnico:
        status_recomendacao = (
            "sugestao_experimental_com_empate_tecnico"
        )

    elif vantagem_moderada:
        status_recomendacao = (
            "sugestao_experimental_com_alternativa_forte"
        )

    else:
        status_recomendacao = (
            "sugestao_tamanho_experimental_calculada"
        )

    return {
        "status": (
            status_recomendacao
        ),

        "disponivel": True,

        "tamanho": (
            tamanho_sugerido
        ),

        "tamanho_sugerido": (
            tamanho_sugerido
        ),

        "tamanho_alternativo": (
            tamanho_alternativo
        ),

        "empate_tecnico": (
            empate_tecnico
        ),

        "alternativa_forte": (
            alternativa_forte
        ),

        "decisao_unica": (
            decisao_unica
        ),

        "preferencia_caimento": (
            preferencia
        ),

        "modelagem": (
            modelagem_normalizada
        ),

        "ranking_parcial": False,

        "dimensoes_utilizadas": [
            "largura",
            "comprimento",
        ],

        "dimensoes_pendentes": [],

        "metrica_horizontal_utilizada": (
            origem_largura
        ),

        "metrica_vertical_utilizada": (
            origem_comprimento
        ),

        "calibracao_vestuario": {
            "status": calibracao_vestuario.get(
                "status"
            ),
            "qualidade": calibracao_vestuario.get(
                "qualidade"
            ),
            "experimental": calibracao_vestuario.get(
                "experimental",
                True,
            ),
            "versao": calibracao_vestuario.get(
                "versao"
            ),
        },

        "alvos_utilizados": {
            "indice_largura": (
                indice_largura_alvo
            ),
            "indice_comprimento": (
                indice_comprimento_alvo
            ),
            "peso_largura": (
                peso_largura_efetivo
            ),
            "peso_comprimento": (
                peso_comprimento_efetivo
            ),
            "modelagem": (
                modelagem_normalizada
            ),
            "fator_modelagem_largura": (
                configuracao.get(
                    "fator_modelagem_largura"
                )
            ),
            "fator_modelagem_comprimento": (
                configuracao.get(
                    "fator_modelagem_comprimento"
                )
            ),
        },

        "medidas_corporais_referencia": {
            "largura_corporal_vestuario_cm": round(
                largura_corporal_cm,
                2,
            ),
            "comprimento_corporal_vestuario_cm": round(
                comprimento_corporal_cm,
                2,
            ),
            "origem_horizontal": (
                origem_largura
            ),
            "origem_vertical": (
                origem_comprimento
            ),
        },

        "pontuacao": (
            melhor.get(
                "pontuacao"
            )
        ),

        "pontuacao_melhor_tamanho": (
            melhor.get(
                "pontuacao"
            )
        ),

        "ranking": (
            ranking
        ),

        "confianca_ranking": (
            confianca_ranking
        ),

        "zona_decisao": (
            zona_decisao
        ),

        "explicacao_decisao": (
            explicacao_decisao
        ),

        "nivel": (
            "experimental_completo"
        ),

        "recomendacao_definitiva": False,

        "sugestao_experimental": True,

        "mensagem": (
            mensagem_final
        ),

        "mensagem_transparencia": (
            "A sugestão utiliza a calibração "
            "experimental de vestuário do VesteIA "
            "e considera a modelagem real da peça. "
            "Empates técnicos e vantagens moderadas "
            "preservam uma segunda opção relevante "
            "em vez de transformar diferenças "
            "matemáticas pequenas ou intermediárias "
            "em decisões isoladas. Apenas uma "
            "vantagem clara permite decisão única "
            "dentro do ranking experimental. "
            "A análise ainda não representa uma "
            "recomendação antropométrica definitiva."
        ),
    }