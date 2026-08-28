def avaliar_plausibilidade_medida(
    nome_medida,
    valor_cm,
):
    """
    Avalia se uma medida corporal estimada está
    dentro de uma faixa plausível para uso experimental.

    IMPORTANTE:
    as faixas abaixo são filtros internos de sanidade.

    Elas NÃO representam:
    - padrão clínico;
    - antropometria oficial;
    - circunferência corporal real;
    - medida definitiva para recomendação de tamanho.
    """

    if valor_cm is None:
        return {
            "status": "medida_indisponivel",
            "plausivel": False,
            "valor_cm": None,
        }

    try:
        valor_cm = float(
            valor_cm
        )

    except (
        TypeError,
        ValueError,
    ):
        return {
            "status": "medida_invalida",
            "plausivel": False,
            "valor_cm": None,
        }

    if valor_cm <= 0:
        return {
            "status": "medida_invalida",
            "plausivel": False,
            "valor_cm": round(
                valor_cm,
                2,
            ),
        }

    faixas = {
        "largura_ombros_cm": {
            "min": 25.0,
            "max": 70.0,
        },

        "largura_quadril_cm": {
            "min": 15.0,
            "max": 65.0,
        },

        "largura_torax_cm": {
            "min": 20.0,
            "max": 70.0,
        },

        "comprimento_tronco_cm": {
            "min": 30.0,
            "max": 90.0,
        },
    }

    faixa = (
        faixas.get(
            nome_medida
        )
    )

    if faixa is None:
        return {
            "status": "medida_nao_configurada",
            "plausivel": False,
            "valor_cm": round(
                valor_cm,
                2,
            ),
        }

    plausivel = (
        faixa["min"]
        <= valor_cm
        <= faixa["max"]
    )

    if plausivel:
        status = (
            "medida_plausivel"
        )

    else:
        status = (
            "medida_fora_da_faixa"
        )

    return {
        "status": status,

        "plausivel": (
            plausivel
        ),

        "valor_cm": round(
            valor_cm,
            2,
        ),

        "faixa_min_cm": (
            faixa["min"]
        ),

        "faixa_max_cm": (
            faixa["max"]
        ),
    }


def gerar_medidas_corporais_calibradas(
    medidas_corporais_estimadas,
    calibracao_anatomica,
    fator_calibracao_metrica,
    consistencia_geometrica,
):
    """
    Consolida as medidas corporais disponíveis
    depois das validações atuais do pipeline.

    Sprint 48:
    - mantém separação entre medida visual e medida anatômica;
    - valida ombros, quadril, tórax e tronco;
    - não libera as medidas como antropometria real;
    - não marca nenhuma medida como corrigida anatomicamente.

    Mesmo após validações, os valores continuam sendo
    estimativas visuais experimentais.
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

    largura_torax_cm = (
        medidas_corporais_estimadas.get(
            "largura_torax_cm"
        )
    )

    comprimento_tronco_cm = (
        medidas_corporais_estimadas.get(
            "comprimento_tronco_cm"
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

    avaliacao_torax = (
        avaliar_plausibilidade_medida(
            "largura_torax_cm",
            largura_torax_cm,
        )
    )

    avaliacao_tronco = (
        avaliar_plausibilidade_medida(
            "comprimento_tronco_cm",
            comprimento_tronco_cm,
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

    torax_plausivel = (
        avaliacao_torax.get(
            "plausivel",
            False,
        )
    )

    tronco_plausivel = (
        avaliacao_tronco.get(
            "plausivel",
            False,
        )
    )

    validacoes_estruturais_ok = (
        calibracao_pronta
        and fator_liberado
        and geometria_consistente
    )

    medidas_basicas_plausiveis = (
        ombros_plausiveis
        and quadril_plausivel
        and torax_plausivel
        and tronco_plausivel
    )

    validacoes_ok = (
        validacoes_estruturais_ok
        and medidas_basicas_plausiveis
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
            "distancia_quadris_fora_da_faixa"
        )

    if not torax_plausivel:
        motivos.append(
            "largura_torax_visual_fora_da_faixa"
        )

    if not tronco_plausivel:
        motivos.append(
            "comprimento_tronco_fora_da_faixa"
        )

    if validacoes_ok:
        status = (
            "medidas_visuais_validadas"
        )

    elif validacoes_estruturais_ok:
        status = (
            "medidas_com_ressalvas"
        )

    else:
        status = (
            "medidas_nao_liberadas"
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

        "largura_torax_cm": (
            largura_torax_cm
        ),

        "comprimento_tronco_cm": (
            comprimento_tronco_cm
        ),

        "avaliacao_plausibilidade": {
            "ombros": (
                avaliacao_ombros
            ),

            "quadril": (
                avaliacao_quadril
            ),

            "torax": (
                avaliacao_torax
            ),

            "tronco": (
                avaliacao_tronco
            ),
        },

        "origem": (
            "estimativa_visual_validada"
        ),

        "precisao": (
            "experimental"
        ),

        "correcao_geometrica_2d_aplicada": (
            medidas_corporais_estimadas.get(
                "correcao_geometrica_2d_aplicada",
                False,
            )
        ),

        "aspect_ratio_aplicado": (
            medidas_corporais_estimadas.get(
                "aspect_ratio_aplicado"
            )
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
            "As medidas foram validadas quanto à "
            "consistência visual e plausibilidade. "
            "Elas ainda representam projeções "
            "geométricas experimentais e não "
            "medidas antropométricas exatas."
        ),
    }


def avaliar_pose_para_correcao_anatomica(
    pontos_corporais,
    consistencia_geometrica,
):
    """
    Avalia se a pose possui condições
    mínimas para futuras correções métricas.

    Analisa:
    - assimetria de profundidade dos ombros;
    - assimetria de profundidade do quadril;
    - alinhamento vertical dos ombros;
    - alinhamento vertical do quadril.

    Nenhuma medida é corrigida nesta função.
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
        ponto = (
            pontos_corporais.get(
                nome
            )
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
                    (
                        f"{nome}_indisponivel_"
                        "ou_nao_confiavel"
                    )
                ],
            }

        pontos[nome] = ponto

    ombro_esquerdo = (
        pontos[
            "ombro_esquerdo"
        ]
    )

    ombro_direito = (
        pontos[
            "ombro_direito"
        ]
    )

    quadril_esquerdo = (
        pontos[
            "quadril_esquerdo"
        ]
    )

    quadril_direito = (
        pontos[
            "quadril_direito"
        ]
    )

    diferenca_z_ombros = abs(
        ombro_esquerdo["z"]
        - ombro_direito["z"]
    )

    diferenca_z_quadril = abs(
        quadril_esquerdo["z"]
        - quadril_direito["z"]
    )

    diferenca_y_ombros = abs(
        ombro_esquerdo["y"]
        - ombro_direito["y"]
    )

    diferenca_y_quadril = abs(
        quadril_esquerdo["y"]
        - quadril_direito["y"]
    )

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

        "motivos": motivos,

        "mensagem": (
            "Pose corporal avaliada para futura "
            "correção anatômica das medidas."
        ),
    }


def calcular_indice_distorcao_perspectiva(
    pose_para_correcao_anatomica,
):
    """
    Calcula um índice interno de distorção
    geométrica da captura.

    O índice não representa perspectiva física
    em graus ou distância real da câmera.

    Serve como indicador interno de qualidade
    para o pipeline do VesteIA.
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
            {},
        )
    )

    diferenca_z_ombros = (
        metricas.get(
            "diferenca_z_ombros"
        )
    )

    diferenca_z_quadril = (
        metricas.get(
            "diferenca_z_quadril"
        )
    )

    diferenca_y_ombros = (
        metricas.get(
            "diferenca_y_ombros"
        )
    )

    diferenca_y_quadril = (
        metricas.get(
            "diferenca_y_quadril"
        )
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

    correcao_metrica_segura = (
        pose_apta
        and nivel == "baixa"
    )

    return {
        "status": (
            "distorcao_avaliada"
        ),

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
            "avaliada. O índice representa "
            "qualidade visual relativa e não "
            "uma correção métrica da anatomia."
        ),
    }


def calcular_confianca_metrica(
    medidas_corporais_estimadas,
    calibracao_anatomica,
    consistencia_geometrica,
    pose_para_correcao_anatomica,
    indice_distorcao_perspectiva,
):
    """
    Calcula uma confiança específica para
    o uso métrico das medidas corporais.

    Esta confiança é diferente da confiança visual.

    Considera:
    - existência das medidas;
    - calibração;
    - consistência geométrica;
    - qualidade da pose;
    - distorção;
    - correção de aspect ratio.
    """

    pontuacao = 0.0
    motivos = []

    if not medidas_corporais_estimadas:
        return {
            "status": "dados_insuficientes",
            "nivel": "indisponivel",
            "pontuacao": 0,
            "motivos": [
                "medidas_corporais_ausentes"
            ],
        }

    correcao_geometrica = (
        medidas_corporais_estimadas.get(
            "correcao_geometrica_2d_aplicada",
            False,
        )
    )

    if correcao_geometrica:
        pontuacao += 0.20
        motivos.append(
            "correcao_geometrica_2d_aplicada"
        )

    else:
        motivos.append(
            "correcao_geometrica_2d_indisponivel"
        )

    calibracao_pronta = (
        calibracao_anatomica.get(
            "pronta_para_calibracao_anatomica",
            False,
        )
        if calibracao_anatomica
        else False
    )

    if calibracao_pronta:
        pontuacao += 0.20
        motivos.append(
            "calibracao_anatomica_validada"
        )

    else:
        motivos.append(
            "calibracao_anatomica_nao_validada"
        )

    geometria_consistente = (
        consistencia_geometrica.get(
            "consistente",
            False,
        )
        if consistencia_geometrica
        else False
    )

    if geometria_consistente:
        pontuacao += 0.20
        motivos.append(
            "geometria_consistente"
        )

    else:
        motivos.append(
            "geometria_inconsistente"
        )

    pose_apta = (
        pose_para_correcao_anatomica.get(
            "pose_apta",
            False,
        )
        if pose_para_correcao_anatomica
        else False
    )

    if pose_apta:
        pontuacao += 0.20
        motivos.append(
            "pose_apta"
        )

    else:
        motivos.append(
            "pose_com_limitacoes"
        )

    nivel_distorcao = (
        indice_distorcao_perspectiva.get(
            "nivel_distorcao",
            "indisponivel",
        )
        if indice_distorcao_perspectiva
        else "indisponivel"
    )

    if nivel_distorcao == "baixa":
        pontuacao += 0.20
        motivos.append(
            "distorcao_baixa"
        )

    elif nivel_distorcao == "moderada":
        pontuacao += 0.12
        motivos.append(
            "distorcao_moderada"
        )

    elif nivel_distorcao == "alta":
        pontuacao += 0.04
        motivos.append(
            "distorcao_alta"
        )

    else:
        motivos.append(
            "distorcao_indisponivel"
        )

    pontuacao = round(
        min(
            pontuacao,
            1.0,
        ),
        4,
    )

    if pontuacao >= 0.85:
        nivel = "alta"

    elif pontuacao >= 0.65:
        nivel = "moderada"

    elif pontuacao > 0:
        nivel = "baixa"

    else:
        nivel = "indisponivel"

    return {
        "status": (
            "confianca_metrica_calculada"
        ),

        "nivel": (
            nivel
        ),

        "pontuacao": (
            pontuacao
        ),

        "nivel_distorcao": (
            nivel_distorcao
        ),

        "correcao_geometrica_2d_aplicada": (
            correcao_geometrica
        ),

        "calibracao_anatomica_pronta": (
            calibracao_pronta
        ),

        "geometria_consistente": (
            geometria_consistente
        ),

        "pose_apta": (
            pose_apta
        ),

        "motivos": (
            motivos
        ),

        "mensagem": (
            "Confiança métrica experimental "
            "calculada com base na qualidade "
            "geométrica e na captura."
        ),
    }


def gerar_metricas_corporais_para_vestuario(
    medidas_corporais_estimadas,
    indice_distorcao_perspectiva,
    calibracao_anatomica,
    consistencia_geometrica=None,
    pose_para_correcao_anatomica=None,
):
    """
    Classifica semanticamente as medidas
    corporais disponíveis.

    Esta função é fundamental para impedir
    comparações incompatíveis entre:

    - distâncias de landmarks;
    - projeções frontais;
    - comprimentos corporais;
    - medidas cadastradas de uma roupa.

    Neste estágio:
    - ombros NÃO são usados diretamente como largura da roupa;
    - quadril NÃO é tratado como circunferência;
    - tórax frontal NÃO é tratado como meia circunferência;
    - comprimento do tronco pode participar de comparação
      vertical experimental.
    """

    if not medidas_corporais_estimadas:
        return {
            "status": (
                "medidas_indisponiveis"
            ),

            "metricas_liberadas": False,

            "uso_para_recomendacao_tamanho": False,

            "medidas": {},
        }

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

    largura_torax_cm = (
        medidas_corporais_estimadas.get(
            "largura_torax_cm"
        )
    )

    comprimento_tronco_cm = (
        medidas_corporais_estimadas.get(
            "comprimento_tronco_cm"
        )
    )

    nivel_distorcao = (
        indice_distorcao_perspectiva.get(
            "nivel_distorcao",
            "indisponivel",
        )
        if indice_distorcao_perspectiva
        else "indisponivel"
    )

    calibracao_pronta = (
        calibracao_anatomica.get(
            "pronta_para_calibracao_anatomica",
            False,
        )
        if calibracao_anatomica
        else False
    )

    geometria_consistente = (
        consistencia_geometrica.get(
            "consistente",
            False,
        )
        if consistencia_geometrica
        else False
    )

    pose_apta = (
        pose_para_correcao_anatomica.get(
            "pose_apta",
            False,
        )
        if pose_para_correcao_anatomica
        else False
    )

    correcao_geometrica = (
        medidas_corporais_estimadas.get(
            "correcao_geometrica_2d_aplicada",
            False,
        )
    )

    medidas = {
        "ombros": {
            "valor_cm": (
                largura_ombros_cm
            ),

            "tipo": (
                "distancia_landmarks"
            ),

            "natureza": (
                "largura_frontal_observada"
            ),

            "origem": (
                "landmarks_ombros"
            ),

            "uso_direto_em_roupa": (
                False
            ),

            "uso_experimental": (
                "analise_proporcional"
            ),
        },

        "quadril": {
            "valor_cm": (
                largura_quadril_cm
            ),

            "tipo": (
                "distancia_landmarks"
            ),

            "natureza": (
                "distancia_entre_landmarks"
            ),

            "origem": (
                "landmarks_quadril"
            ),

            "uso_direto_em_roupa": (
                False
            ),

            "uso_experimental": (
                "analise_proporcional"
            ),
        },

        "torax": {
            "valor_cm": (
                largura_torax_cm
            ),

            "tipo": (
                "estimativa_interpolada"
            ),

            "natureza": (
                "largura_frontal_observada"
            ),

            "origem": (
                "interpolacao_ombros_quadril"
            ),

            "uso_direto_em_roupa": (
                False
            ),

            "uso_experimental": (
                "analise_visual_do_tronco"
            ),

            "observacao": (
                "Não representa circunferência "
                "do tórax nem meia circunferência."
            ),
        },

        "tronco": {
            "valor_cm": (
                comprimento_tronco_cm
            ),

            "tipo": (
                "distancia_vertical_corporal"
            ),

            "natureza": (
                "comprimento_corporal_observado"
            ),

            "origem": (
                "centro_ombros_ate_centro_quadris"
            ),

            "uso_direto_em_roupa": (
                True
            ),

            "uso_experimental": (
                "comparacao_vertical"
            ),
        },
    }

    quantidade_disponivel = sum(
        1
        for medida in (
            medidas.values()
        )
        if (
            medida.get(
                "valor_cm"
            )
            is not None
        )
    )

    if quantidade_disponivel == 0:
        status = (
            "metricas_indisponiveis"
        )

        metricas_liberadas = (
            False
        )

    elif not calibracao_pronta:
        status = (
            "metricas_com_ressalvas"
        )

        metricas_liberadas = (
            False
        )

    elif not geometria_consistente:
        status = (
            "metricas_geometricamente_inconsistentes"
        )

        metricas_liberadas = (
            False
        )

    elif nivel_distorcao == "alta":
        status = (
            "metricas_com_distorcao_alta"
        )

        metricas_liberadas = (
            False
        )

    else:
        status = (
            "metricas_visuais_validadas"
        )

        metricas_liberadas = (
            True
        )

    metricas_para_comparacao_direta = [
        nome
        for (
            nome,
            medida,
        ) in medidas.items()
        if (
            medida.get(
                "uso_direto_em_roupa",
                False,
            )
            and
            medida.get(
                "valor_cm"
            )
            is not None
        )
    ]

    metricas_apenas_visuais = [
        nome
        for (
            nome,
            medida,
        ) in medidas.items()
        if (
            not medida.get(
                "uso_direto_em_roupa",
                False,
            )
            and
            medida.get(
                "valor_cm"
            )
            is not None
        )
    ]

    return {
        "status": (
            status
        ),

        "metricas_liberadas": (
            metricas_liberadas
        ),

        "medidas": (
            medidas
        ),

        "metricas_para_comparacao_direta": (
            metricas_para_comparacao_direta
        ),

        "metricas_apenas_visuais": (
            metricas_apenas_visuais
        ),

        "qualidade": {
            "calibracao_anatomica_pronta": (
                calibracao_pronta
            ),

            "geometria_consistente": (
                geometria_consistente
            ),

            "pose_apta": (
                pose_apta
            ),

            "nivel_distorcao": (
                nivel_distorcao
            ),

            "correcao_geometrica_2d_aplicada": (
                correcao_geometrica
            ),
        },

        "uso_para_recomendacao_tamanho": (
            False
        ),

        "mensagem": (
            "As medidas corporais foram classificadas "
            "pela natureza geométrica. Projeções "
            "frontais e distâncias entre landmarks "
            "não são tratadas como circunferências "
            "corporais ou larguras equivalentes "
            "às medidas cadastradas da roupa."
        ),
    }