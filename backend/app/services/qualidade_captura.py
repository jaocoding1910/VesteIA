def avaliar_qualidade_captura(
    qualidade_regioes,
    calibracao_corporal,
    pose_para_correcao_anatomica,
    indice_distorcao_perspectiva,
):
    """
    Consolida diferentes sinais do pipeline visual
    e decide se a captura pode avançar.

    Decisões possíveis:
    - avancar
    - avancar_com_ressalvas
    - pedir_nova_foto

    Esta função avalia qualidade da captura.
    Ela NÃO recomenda tamanho e NÃO corrige
    medidas corporais.
    """

    if not qualidade_regioes:
        return {
            "status": "dados_insuficientes",
            "pontuacao": 0,
            "nivel": "insuficiente",
            "decisao": "pedir_nova_foto",
            "nova_foto_necessaria": True,
            "orientacoes": [
                "Envie uma nova foto com o corpo visível."
            ],
        }

    # ======================================================
    # QUALIDADE DAS REGIÕES
    # ======================================================

    regioes_importantes = (
        "tronco",
        "pernas",
        "pes",
    )

    percentuais = []

    for regiao in regioes_importantes:

        qualidade = (
            qualidade_regioes.get(
                regiao,
                {}
            )
        )

        percentual = qualidade.get(
            "percentual_confiavel",
            0,
        )

        percentuais.append(
            percentual
        )

    qualidade_media_regioes = round(
        sum(percentuais)
        / len(percentuais),
        4,
    )

    # ======================================================
    # CORPO INTEIRO
    # ======================================================

    corpo_inteiro_visivel = (
        calibracao_corporal.get(
            "corpo_inteiro_visivel",
            False,
        )
        if calibracao_corporal
        else False
    )

    # ======================================================
    # POSE
    # ======================================================

    pose_apta = (
        pose_para_correcao_anatomica.get(
            "pose_apta",
            False,
        )
        if pose_para_correcao_anatomica
        else False
    )

    # ======================================================
    # DISTORÇÃO
    # ======================================================

    nivel_distorcao = (
        indice_distorcao_perspectiva.get(
            "nivel_distorcao",
            "indisponivel",
        )
        if indice_distorcao_perspectiva
        else "indisponivel"
    )

    mapa_distorcao = {
        "baixa": 1.0,
        "moderada": 0.7,
        "alta": 0.3,
        "indisponivel": 0.0,
    }

    score_distorcao = (
        mapa_distorcao.get(
            nivel_distorcao,
            0.0,
        )
    )

    # ======================================================
    # SCORE FINAL
    # ======================================================

    score_corpo_inteiro = (
        1.0
        if corpo_inteiro_visivel
        else 0.0
    )

    score_pose = (
        1.0
        if pose_apta
        else 0.0
    )

    pontuacao = (
        qualidade_media_regioes * 0.40
        + score_corpo_inteiro * 0.25
        + score_pose * 0.20
        + score_distorcao * 0.15
    )

    pontuacao = round(
        pontuacao,
        4,
    )

    # ======================================================
    # DECISÃO
    # ======================================================

    if (
        pontuacao >= 0.90
        and corpo_inteiro_visivel
        and pose_apta
        and nivel_distorcao == "baixa"
    ):
        nivel = "excelente"
        decisao = "avancar"
        nova_foto_necessaria = False

    elif (
        pontuacao >= 0.70
        and corpo_inteiro_visivel
        and pose_apta
    ):
        nivel = "boa"
        decisao = "avancar_com_ressalvas"
        nova_foto_necessaria = False

    else:
        nivel = "insuficiente"
        decisao = "pedir_nova_foto"
        nova_foto_necessaria = True

    # ======================================================
    # ORIENTAÇÕES AO USUÁRIO
    # ======================================================

    orientacoes = []

    if not corpo_inteiro_visivel:
        orientacoes.append(
            "Mostre o corpo inteiro, incluindo os pés."
        )

    if not pose_apta:
        orientacoes.append(
            "Fique mais de frente para a câmera e mantenha "
            "ombros e quadris alinhados."
        )

    if nivel_distorcao == "moderada":
        orientacoes.append(
            "Tente posicionar a câmera mais centralizada "
            "e paralela ao corpo."
        )

    elif nivel_distorcao == "alta":
        orientacoes.append(
            "Refaça a foto com a câmera centralizada, "
            "sem inclinação e mais distante do corpo."
        )

    if qualidade_media_regioes < 0.75:
        orientacoes.append(
            "Garanta que tronco, pernas e pés estejam "
            "claramente visíveis."
        )

    if not orientacoes:
        orientacoes.append(
            "Captura adequada para continuar a análise."
        )

    return {
        "status": "avaliada",

        "pontuacao": (
            pontuacao
        ),

        "nivel": (
            nivel
        ),

        "decisao": (
            decisao
        ),

        "nova_foto_necessaria": (
            nova_foto_necessaria
        ),

        "componentes": {
            "qualidade_media_regioes": (
                qualidade_media_regioes
            ),

            "corpo_inteiro_visivel": (
                corpo_inteiro_visivel
            ),

            "pose_apta": (
                pose_apta
            ),

            "nivel_distorcao": (
                nivel_distorcao
            ),

            "score_distorcao": (
                score_distorcao
            ),
        },

        "orientacoes": (
            orientacoes
        ),

        "mensagem": (
            "Qualidade geral da captura avaliada "
            "pelo pipeline visual do VesteIA."
        ),
    }