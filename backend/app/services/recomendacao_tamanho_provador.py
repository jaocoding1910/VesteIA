def _normalizar_preferencia_caimento(
    preferencia_caimento,
):
    """
    Normaliza a preferência de caimento
    utilizada pelo Provador VesteIA.

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


def _obter_alvos_preferencia(
    preferencia_caimento,
):
    """
    Define os índices relativos desejados
    para cada preferência de caimento.

    índice largura:
        largura da peça /
        largura visual do tórax

    índice comprimento:
        comprimento da peça /
        comprimento visual do tronco

    Estes valores ainda são experimentais.
    """

    preferencia = (
        _normalizar_preferencia_caimento(
            preferencia_caimento
        )
    )

    configuracoes = {
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

    return {
        "preferencia": preferencia,
        **configuracoes[
            preferencia
        ],
    }


def _calcular_score(
    indice,
    alvo,
    tolerancia,
):
    """
    Calcula uma pontuação entre 0 e 1.

    Quanto mais próximo do alvo,
    maior a pontuação.
    """

    if indice is None:
        return 0

    diferenca = abs(
        indice - alvo
    )

    score = (
        1
        - (
            diferenca
            / tolerancia
        )
    )

    if score < 0:
        score = 0

    if score > 1:
        score = 1

    return round(
        score,
        4,
    )


def _classificar_largura(
    indice_largura,
):
    """
    Interpreta visualmente
    a relação entre largura da peça
    e largura do tórax.
    """

    if indice_largura is None:
        return "indisponivel"

    if indice_largura < 1.03:
        return "ajustado"

    if indice_largura < 1.15:
        return "equilibrado"

    return "amplo"


def _classificar_comprimento(
    indice_comprimento,
):
    """
    Interpreta visualmente
    a relação entre comprimento da peça
    e comprimento do tronco.
    """

    if indice_comprimento is None:
        return "indisponivel"

    if indice_comprimento < 1.12:
        return "curto"

    if indice_comprimento < 1.20:
        return "equilibrado"

    return "alongado"


def _resultado_ranking(
    posicao,
    caimento_largura,
):
    """
    Gera um rótulo simples
    para cada posição do ranking.
    """

    if posicao == 1:
        return "melhor_equilibrio"

    if (
        caimento_largura
        == "amplo"
    ):
        return (
            "alternativa_mais_ampla"
        )

    if (
        caimento_largura
        == "ajustado"
    ):
        return (
            "alternativa_mais_ajustada"
        )

    return "alternativa"


def gerar_recomendacao_tamanho_provador(
    variacoes_produto,
    deteccao,
    preferencia_caimento="padrao",
):
    """
    Compara todas as variações disponíveis
    do mesmo produto com as medidas corporais
    obtidas pelo Provador VesteIA.

    A preferência do usuário modifica
    os alvos do algoritmo.

    Preferências:
    - justo
    - padrao
    - solto

    O resultado continua sendo experimental.
    """

    if not variacoes_produto:
        return {
            "status": (
                "variacoes_indisponiveis"
            ),

            "disponivel": False,

            "tamanho": None,

            "tamanho_sugerido": None,

            "preferencia_caimento": (
                _normalizar_preferencia_caimento(
                    preferencia_caimento
                )
            ),

            "pontuacao": None,

            "pontuacao_melhor_tamanho": None,

            "ranking": [],

            "nivel": "indisponivel",

            "recomendacao_definitiva": False,

            "mensagem": (
                "Não existem variações "
                "suficientes para comparar "
                "os tamanhos."
            ),

            "mensagem_transparencia": (
                "Não foi possível calcular "
                "uma sugestão de tamanho."
            ),
        }

    medidas = (
        deteccao.get(
            "medidas_corporais_calibradas"
        )
        or deteccao.get(
            "medidas_corporais_estimadas"
        )
        or {}
    )

    largura_torax_cm = (
        medidas.get(
            "largura_torax_cm"
        )
    )

    comprimento_tronco_cm = (
        medidas.get(
            "comprimento_tronco_cm"
        )
    )

    if (
        largura_torax_cm is None
        or comprimento_tronco_cm
        is None
    ):
        return {
            "status": (
                "medidas_corporais_insuficientes"
            ),

            "disponivel": False,

            "tamanho": None,

            "tamanho_sugerido": None,

            "preferencia_caimento": (
                _normalizar_preferencia_caimento(
                    preferencia_caimento
                )
            ),

            "pontuacao": None,

            "pontuacao_melhor_tamanho": None,

            "ranking": [],

            "nivel": "indisponivel",

            "recomendacao_definitiva": False,

            "mensagem": (
                "Ainda não existem medidas "
                "corporais suficientes para "
                "comparar os tamanhos."
            ),

            "mensagem_transparencia": (
                "O VesteIA precisa de medidas "
                "corporais válidas antes de "
                "comparar os tamanhos."
            ),
        }

    try:
        largura_torax_cm = float(
            largura_torax_cm
        )

        comprimento_tronco_cm = float(
            comprimento_tronco_cm
        )

    except (
        TypeError,
        ValueError,
    ):
        return {
            "status": (
                "medidas_corporais_invalidas"
            ),

            "disponivel": False,

            "tamanho": None,

            "tamanho_sugerido": None,

            "preferencia_caimento": (
                _normalizar_preferencia_caimento(
                    preferencia_caimento
                )
            ),

            "pontuacao": None,

            "pontuacao_melhor_tamanho": None,

            "ranking": [],

            "nivel": "indisponivel",

            "recomendacao_definitiva": False,

            "mensagem": (
                "As medidas corporais disponíveis "
                "não são válidas para comparação."
            ),

            "mensagem_transparencia": (
                "Não foi possível calcular "
                "uma sugestão de tamanho."
            ),
        }

    if (
        largura_torax_cm <= 0
        or comprimento_tronco_cm <= 0
    ):
        return {
            "status": (
                "medidas_corporais_invalidas"
            ),

            "disponivel": False,

            "tamanho": None,

            "tamanho_sugerido": None,

            "preferencia_caimento": (
                _normalizar_preferencia_caimento(
                    preferencia_caimento
                )
            ),

            "pontuacao": None,

            "pontuacao_melhor_tamanho": None,

            "ranking": [],

            "nivel": "indisponivel",

            "recomendacao_definitiva": False,

            "mensagem": (
                "As medidas corporais disponíveis "
                "não são válidas para comparação."
            ),

            "mensagem_transparencia": (
                "Não foi possível calcular "
                "uma sugestão de tamanho."
            ),
        }

    configuracao = (
        _obter_alvos_preferencia(
            preferencia_caimento
        )
    )

    preferencia = (
        configuracao[
            "preferencia"
        ]
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

    peso_largura = (
        configuracao[
            "peso_largura"
        ]
    )

    peso_comprimento = (
        configuracao[
            "peso_comprimento"
        ]
    )

    ranking = []

    for produto in variacoes_produto:
        largura_peca_cm = (
            produto.get(
                "largura_cm"
            )
        )

        comprimento_peca_cm = (
            produto.get(
                "comprimento_cm"
            )
        )

        if (
            largura_peca_cm is None
            or comprimento_peca_cm
            is None
        ):
            continue

        try:
            largura_peca_cm = float(
                largura_peca_cm
            )

            comprimento_peca_cm = float(
                comprimento_peca_cm
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        if (
            largura_peca_cm <= 0
            or comprimento_peca_cm <= 0
        ):
            continue

        indice_largura = (
            largura_peca_cm
            / largura_torax_cm
        )

        indice_comprimento = (
            comprimento_peca_cm
            / comprimento_tronco_cm
        )

        score_largura = (
            _calcular_score(
                indice=(
                    indice_largura
                ),

                alvo=(
                    indice_largura_alvo
                ),

                tolerancia=0.30,
            )
        )

        score_comprimento = (
            _calcular_score(
                indice=(
                    indice_comprimento
                ),

                alvo=(
                    indice_comprimento_alvo
                ),

                tolerancia=0.35,
            )
        )

        pontuacao = (
            (
                score_largura
                * peso_largura
            )
            +
            (
                score_comprimento
                * peso_comprimento
            )
        )

        caimento_largura = (
            _classificar_largura(
                indice_largura
            )
        )

        caimento_comprimento = (
            _classificar_comprimento(
                indice_comprimento
            )
        )

        ranking.append(
            {
                "produto_id": (
                    produto.get(
                        "id"
                    )
                ),

                "tamanho": (
                    produto.get(
                        "tamanho"
                    )
                ),

                "largura_peca_cm": round(
                    largura_peca_cm,
                    2,
                ),

                "comprimento_peca_cm": round(
                    comprimento_peca_cm,
                    2,
                ),

                "indice_largura": round(
                    indice_largura,
                    4,
                ),

                "indice_comprimento": round(
                    indice_comprimento,
                    4,
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
            }
        )

    if not ranking:
        return {
            "status": (
                "variacoes_sem_medidas"
            ),

            "disponivel": False,

            "tamanho": None,

            "tamanho_sugerido": None,

            "preferencia_caimento": (
                preferencia
            ),

            "pontuacao": None,

            "pontuacao_melhor_tamanho": None,

            "ranking": [],

            "nivel": "indisponivel",

            "recomendacao_definitiva": False,

            "mensagem": (
                "As variações encontradas "
                "não possuem medidas suficientes "
                "para comparação."
            ),

            "mensagem_transparencia": (
                "Não foi possível calcular "
                "uma sugestão de tamanho."
            ),
        }

    ranking.sort(
        key=lambda item: (
            item[
                "pontuacao"
            ]
        ),
        reverse=True,
    )

    for indice, item in enumerate(
        ranking,
        start=1,
    ):
        item[
            "posicao"
        ] = indice

        item[
            "resultado"
        ] = (
            _resultado_ranking(
                posicao=indice,

                caimento_largura=(
                    item[
                        "caimento_largura"
                    ]
                ),
            )
        )

    melhor = ranking[0]

    tamanho_sugerido = (
        melhor[
            "tamanho"
        ]
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

    return {
        "status": (
            "sugestao_tamanho_calculada"
        ),

        "disponivel": True,

        "tamanho": (
            tamanho_sugerido
        ),

        "tamanho_sugerido": (
            tamanho_sugerido
        ),

        "preferencia_caimento": (
            preferencia
        ),

        "alvos_utilizados": {
            "indice_largura": (
                indice_largura_alvo
            ),

            "indice_comprimento": (
                indice_comprimento_alvo
            ),

            "peso_largura": (
                peso_largura
            ),

            "peso_comprimento": (
                peso_comprimento
            ),
        },

        "medidas_corporais_referencia": {
            "largura_torax_cm": (
                round(
                    largura_torax_cm,
                    2,
                )
            ),

            "comprimento_tronco_cm": (
                round(
                    comprimento_tronco_cm,
                    2,
                )
            ),
        },

        "pontuacao": (
            melhor[
                "pontuacao"
            ]
        ),

        "pontuacao_melhor_tamanho": (
            melhor[
                "pontuacao"
            ]
        ),

        "ranking": (
            ranking
        ),

        "nivel": (
            "experimental"
        ),

        "recomendacao_definitiva": False,

        "mensagem": (
            f"O tamanho {tamanho_sugerido} "
            "apresentou o melhor resultado "
            f"{mensagens_preferencia[preferencia]} "
            "entre as opções disponíveis."
        ),

        "mensagem_transparencia": (
            "Esta sugestão utiliza medidas "
            "corporais visuais experimentais "
            "e ainda não representa uma "
            "recomendação antropométrica "
            "definitiva."
        ),
    }