def avaliar_plausibilidade_medida(
    nome_medida,
    valor_cm,
):
    """
    Avalia se uma medida corporal estimada está
    dentro de uma faixa plausível para uso experimental.

    As faixas abaixo são provisórias e servem apenas
    como filtro de sanidade do pipeline.

    Elas NÃO representam referência clínica,
    antropométrica oficial ou padrão definitivo.
    """

    if valor_cm is None:
        return {
            "status": "medida_indisponivel",
            "plausivel": False,
            "valor_cm": None,
        }

    faixas = {
        "largura_ombros_cm": {
            "min": 30.0,
            "max": 65.0,
        },

        "largura_quadril_cm": {
            "min": 25.0,
            "max": 60.0,
        },
    }

    faixa = faixas.get(
        nome_medida
    )

    if faixa is None:
        return {
            "status": "medida_nao_configurada",
            "plausivel": False,
            "valor_cm": valor_cm,
        }

    plausivel = (
        faixa["min"]
        <= valor_cm
        <= faixa["max"]
    )

    if plausivel:
        status = "medida_plausivel"
    else:
        status = "medida_fora_da_faixa"

    return {
        "status": status,
        "plausivel": plausivel,
        "valor_cm": round(
            valor_cm,
            2,
        ),
        "faixa_min_cm": faixa["min"],
        "faixa_max_cm": faixa["max"],
    }


def gerar_medidas_corporais_calibradas(
    medidas_corporais_estimadas,
    calibracao_anatomica,
    fator_calibracao_metrica,
    consistencia_geometrica,
):
    """
    Consolida as medidas corporais após todas as
    validações atuais do pipeline.

    IMPORTANTE:
    nesta etapa ainda não aplicamos fator anatômico
    empírico ou correção baseada em dataset.

    Portanto, os valores continuam sendo estimativas
    visuais validadas, não medidas antropométricas exatas.
    """

    if not medidas_corporais_estimadas:
        return {
            "status": "medidas_estimadas_indisponiveis",
            "medidas_liberadas": False,
            "uso_para_recomendacao_tamanho": False,
        }

    if not calibracao_anatomica:
        return {
            "status": "calibracao_anatomica_indisponivel",
            "medidas_liberadas": False,
            "uso_para_recomendacao_tamanho": False,
        }

    if not fator_calibracao_metrica:
        return {
            "status": "fator_metrico_indisponivel",
            "medidas_liberadas": False,
            "uso_para_recomendacao_tamanho": False,
        }

    if not consistencia_geometrica:
        return {
            "status": "consistencia_geometrica_indisponivel",
            "medidas_liberadas": False,
            "uso_para_recomendacao_tamanho": False,
        }

    calibracao_pronta = (
        calibracao_anatomica.get(
            "pronta_para_calibracao_anatomica",
            False,
        )
    )

    fator_liberado = (
        fator_calibracao_metrica.get(
            "calibracao_liberada",
            False,
        )
    )

    geometria_consistente = (
        consistencia_geometrica.get(
            "consistente",
            False,
        )
    )

    largura_ombros_cm = (
        medidas_corporais_estimadas.get(
            "largura_ombros_cm"
        )
    )

    largura_quadril_cm = (
        medidas_corporais_estimadas.get(
            "largura_quadril_cm"
        )
    )

    avaliacao_ombros = (
        avaliar_plausibilidade_medida(
            "largura_ombros_cm",
            largura_ombros_cm,
        )
    )

    avaliacao_quadril = (
        avaliar_plausibilidade_medida(
            "largura_quadril_cm",
            largura_quadril_cm,
        )
    )

    ombros_plausiveis = (
        avaliacao_ombros.get(
            "plausivel",
            False,
        )
    )

    quadril_plausivel = (
        avaliacao_quadril.get(
            "plausivel",
            False,
        )
    )

    validacoes_ok = (
        calibracao_pronta
        and fator_liberado
        and geometria_consistente
        and ombros_plausiveis
        and quadril_plausivel
    )

    motivos = []

    if not calibracao_pronta:
        motivos.append(
            "calibracao_anatomica_nao_pronta"
        )

    if not fator_liberado:
        motivos.append(
            "fator_calibracao_metrica_nao_liberado"
        )

    if not geometria_consistente:
        motivos.append(
            "geometria_inconsistente"
        )

    if not ombros_plausiveis:
        motivos.append(
            "largura_ombros_fora_da_faixa"
        )

    if not quadril_plausivel:
        motivos.append(
            "largura_quadril_fora_da_faixa"
        )

    if validacoes_ok:
        status = (
            "medidas_visuais_validadas"
        )

    else:
        status = (
            "medidas_com_ressalvas"
        )

    return {
        "status": status,

        "medidas_liberadas": (
            validacoes_ok
        ),

        "largura_ombros_cm": (
            largura_ombros_cm
        ),

        "largura_quadril_cm": (
            largura_quadril_cm
        ),

        "avaliacao_plausibilidade": {
            "ombros": (
                avaliacao_ombros
            ),

            "quadril": (
                avaliacao_quadril
            ),
        },

        "origem": (
            "estimativa_visual_validada"
        ),

        "precisao": (
            "experimental"
        ),

        "medidas_corrigidas_anatomicamente": (
            False
        ),

        "uso_para_recomendacao_tamanho": (
            False
        ),

        "motivos": (
            motivos
        ),

        "mensagem": (
            "As medidas passaram por validações "
            "de consistência e plausibilidade, "
            "mas ainda não possuem correção "
            "anatômica baseada em calibração "
            "empírica ou dataset."
        ),
    }


def avaliar_pose_para_correcao_anatomica(
    pontos_corporais,
    consistencia_geometrica,
):
    """
    Avalia se a pose detectada possui condições
    mínimas para uma futura correção anatômica.

    A função observa principalmente:

    - diferença de profundidade entre os ombros;
    - diferença de profundidade entre os quadris;
    - alinhamento vertical dos ombros;
    - alinhamento vertical dos quadris;
    - consistência geométrica já validada.

    Nenhuma medida corporal é corrigida nesta etapa.

    Os limites utilizados ainda são provisórios
    e devem futuramente ser validados com um
    conjunto maior de imagens.
    """

    if not pontos_corporais:
        return {
            "status": "pontos_corporais_indisponiveis",
            "pose_apta": False,
            "motivos": [
                "pontos_corporais_ausentes"
            ],
        }

    if not consistencia_geometrica:
        return {
            "status": "consistencia_geometrica_indisponivel",
            "pose_apta": False,
            "motivos": [
                "consistencia_geometrica_ausente"
            ],
        }

    if not consistencia_geometrica.get(
        "consistente",
        False,
    ):
        return {
            "status": "geometria_inconsistente",
            "pose_apta": False,
            "motivos": [
                "geometria_corporal_inconsistente"
            ],
        }

    nomes_necessarios = (
        "ombro_esquerdo",
        "ombro_direito",
        "quadril_esquerdo",
        "quadril_direito",
    )

    pontos = {}

    for nome in nomes_necessarios:

        ponto = pontos_corporais.get(
            nome
        )

        if (
            not ponto
            or not ponto.get(
                "confiavel",
                False,
            )
        ):
            return {
                "status": "pontos_essenciais_indisponiveis",
                "pose_apta": False,
                "motivos": [
                    f"{nome}_indisponivel_ou_nao_confiavel"
                ],
            }

        pontos[nome] = ponto

    ombro_esquerdo = pontos[
        "ombro_esquerdo"
    ]

    ombro_direito = pontos[
        "ombro_direito"
    ]

    quadril_esquerdo = pontos[
        "quadril_esquerdo"
    ]

    quadril_direito = pontos[
        "quadril_direito"
    ]

    # ======================================================
    # ASSIMETRIA DE PROFUNDIDADE
    # ======================================================

    diferenca_z_ombros = abs(
        ombro_esquerdo["z"]
        - ombro_direito["z"]
    )

    diferenca_z_quadril = abs(
        quadril_esquerdo["z"]
        - quadril_direito["z"]
    )

    # ======================================================
    # ASSIMETRIA VERTICAL
    # ======================================================

    diferenca_y_ombros = abs(
        ombro_esquerdo["y"]
        - ombro_direito["y"]
    )

    diferenca_y_quadril = abs(
        quadril_esquerdo["y"]
        - quadril_direito["y"]
    )

    # ======================================================
    # LIMITES PROVISÓRIOS
    # ======================================================

    LIMITE_Z_OMBROS = 0.20
    LIMITE_Z_QUADRIL = 0.15

    LIMITE_Y_OMBROS = 0.08
    LIMITE_Y_QUADRIL = 0.06

    ombros_profundidade_ok = (
        diferenca_z_ombros
        <= LIMITE_Z_OMBROS
    )

    quadril_profundidade_ok = (
        diferenca_z_quadril
        <= LIMITE_Z_QUADRIL
    )

    ombros_alinhados = (
        diferenca_y_ombros
        <= LIMITE_Y_OMBROS
    )

    quadril_alinhado = (
        diferenca_y_quadril
        <= LIMITE_Y_QUADRIL
    )

    motivos = []

    if not ombros_profundidade_ok:
        motivos.append(
            "ombros_com_assimetria_de_profundidade"
        )

    if not quadril_profundidade_ok:
        motivos.append(
            "quadril_com_assimetria_de_profundidade"
        )

    if not ombros_alinhados:
        motivos.append(
            "ombros_desalinhados_verticalmente"
        )

    if not quadril_alinhado:
        motivos.append(
            "quadril_desalinhado_verticalmente"
        )

    pose_apta = (
        ombros_profundidade_ok
        and quadril_profundidade_ok
        and ombros_alinhados
        and quadril_alinhado
    )

    if pose_apta:
        status = (
            "pose_apta_para_correcao"
        )

    else:
        status = (
            "pose_com_ressalvas"
        )

    return {
        "status": status,

        "pose_apta": (
            pose_apta
        ),

        "metricas": {
            "diferenca_z_ombros": round(
                diferenca_z_ombros,
                4,
            ),

            "diferenca_z_quadril": round(
                diferenca_z_quadril,
                4,
            ),

            "diferenca_y_ombros": round(
                diferenca_y_ombros,
                4,
            ),

            "diferenca_y_quadril": round(
                diferenca_y_quadril,
                4,
            ),
        },

        "criterios": {
            "ombros_profundidade_ok": (
                ombros_profundidade_ok
            ),

            "quadril_profundidade_ok": (
                quadril_profundidade_ok
            ),

            "ombros_alinhados": (
                ombros_alinhados
            ),

            "quadril_alinhado": (
                quadril_alinhado
            ),
        },

        "motivos": (
            motivos
        ),

        "mensagem": (
            "Pose corporal avaliada para futura "
            "correção anatômica das medidas."
        ),
    }


def calcular_indice_distorcao_perspectiva(
    pose_para_correcao_anatomica,
):
    """
    Calcula um índice experimental de distorção
    geométrica da pose observada.

    O índice NÃO corrige medidas corporais.

    Ele resume as assimetrias de profundidade
    e alinhamento já calculadas pelo pipeline,
    permitindo classificar a captura como:

    - baixa distorção
    - distorção moderada
    - alta distorção

    O objetivo é impedir que medidas obtidas
    em uma pose inadequada sejam tratadas como
    medidas anatômicas confiáveis.
    """

    if not pose_para_correcao_anatomica:
        return {
            "status": "pose_indisponivel",
            "indice_distorcao": None,
            "nivel_distorcao": "indisponivel",
            "correcao_metrica_segura": False,
        }

    metricas = (
        pose_para_correcao_anatomica.get(
            "metricas",
            {}
        )
    )

    diferenca_z_ombros = metricas.get(
        "diferenca_z_ombros"
    )

    diferenca_z_quadril = metricas.get(
        "diferenca_z_quadril"
    )

    diferenca_y_ombros = metricas.get(
        "diferenca_y_ombros"
    )

    diferenca_y_quadril = metricas.get(
        "diferenca_y_quadril"
    )

    valores = (
        diferenca_z_ombros,
        diferenca_z_quadril,
        diferenca_y_ombros,
        diferenca_y_quadril,
    )

    if any(
        valor is None
        for valor in valores
    ):
        return {
            "status": "metricas_incompletas",
            "indice_distorcao": None,
            "nivel_distorcao": "indisponivel",
            "correcao_metrica_segura": False,
        }

    # ======================================================
    # NORMALIZAÇÃO PELOS LIMITES DA ETAPA ANTERIOR
    # ======================================================
    #
    # 1.0 representa aproximadamente o limite
    # máximo aceito pela avaliação de pose.
    #
    # Não é uma medida física de perspectiva.
    # É apenas um indicador interno de qualidade.
    # ======================================================

    score_z_ombros = (
        diferenca_z_ombros
        / 0.20
    )

    score_z_quadril = (
        diferenca_z_quadril
        / 0.15
    )

    score_y_ombros = (
        diferenca_y_ombros
        / 0.08
    )

    score_y_quadril = (
        diferenca_y_quadril
        / 0.06
    )

    indice = (
        score_z_ombros
        + score_z_quadril
        + score_y_ombros
        + score_y_quadril
    ) / 4

    indice = round(
        indice,
        4,
    )

    # ======================================================
    # CLASSIFICAÇÃO EXPERIMENTAL
    # ======================================================

    if indice <= 0.35:
        nivel = "baixa"

    elif indice <= 0.70:
        nivel = "moderada"

    else:
        nivel = "alta"

    pose_apta = (
        pose_para_correcao_anatomica.get(
            "pose_apta",
            False,
        )
    )

    # Mesmo com baixa distorção, ainda não chamamos
    # a medida de anatomicamente corrigida.
    correcao_metrica_segura = (
        pose_apta
        and nivel == "baixa"
    )

    return {
        "status": "distorcao_avaliada",

        "indice_distorcao": (
            indice
        ),

        "nivel_distorcao": (
            nivel
        ),

        "pose_apta": (
            pose_apta
        ),

        "componentes": {
            "profundidade_ombros": round(
                score_z_ombros,
                4,
            ),

            "profundidade_quadril": round(
                score_z_quadril,
                4,
            ),

            "alinhamento_ombros": round(
                score_y_ombros,
                4,
            ),

            "alinhamento_quadril": round(
                score_y_quadril,
                4,
            ),
        },

        "correcao_metrica_segura": (
            correcao_metrica_segura
        ),

        "medidas_corrigidas": False,

        "mensagem": (
            "Distorção geométrica da captura "
            "avaliada. O índice representa qualidade "
            "visual relativa e não uma correção "
            "métrica da anatomia."
        ),
    }