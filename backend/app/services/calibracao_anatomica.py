def avaliar_calibracao_anatomica(
    calibracao_corporal,
    escala_corporal,
    medidas_corporais_estimadas,
    consistencia_geometrica,
):
    """
    Avalia se os dados produzidos pelo pipeline
    visual possuem qualidade suficiente para
    avançar para uma futura calibração anatômica.

    Esta função NÃO corrige medidas e NÃO aplica
    fatores artificiais de ajuste.

    Ela valida:
    - calibração corporal
    - disponibilidade da escala visual
    - existência de medidas estimadas
    - consistência geométrica

    As medidas ainda permanecem provisórias.
    """

    if not calibracao_corporal:
        return {
            "status": "calibracao_corporal_indisponivel",
            "pronta_para_calibracao_anatomica": False,
            "medidas_corrigidas": False,
        }

    if not escala_corporal:
        return {
            "status": "escala_corporal_indisponivel",
            "pronta_para_calibracao_anatomica": False,
            "medidas_corrigidas": False,
        }

    if not medidas_corporais_estimadas:
        return {
            "status": "medidas_corporais_indisponiveis",
            "pronta_para_calibracao_anatomica": False,
            "medidas_corrigidas": False,
        }

    if not consistencia_geometrica:
        return {
            "status": (
                "consistencia_geometrica_indisponivel"
            ),
            "pronta_para_calibracao_anatomica": False,
            "medidas_corrigidas": False,
        }

    calibracao_pronta = (
        calibracao_corporal.get(
            "status"
        )
        == "pronta_para_calibracao"
    )

    escala_disponivel = (
        escala_corporal.get(
            "conversao_disponivel",
            False,
        )
    )

    medidas_calculadas = (
        medidas_corporais_estimadas.get(
            "status"
        )
        in (
            "estimativa_visual_calculada",
            "estimativa_parcial",
        )
    )

    geometria_consistente = (
        consistencia_geometrica.get(
            "consistente",
            False,
        )
    )

    precisao_metrica = (
        escala_corporal.get(
            "precisao_metrica"
        )
    )

    if (
        calibracao_pronta
        and escala_disponivel
        and medidas_calculadas
        and geometria_consistente
    ):
        return {
            "status": (
                "dados_visuais_validados"
            ),

            "pronta_para_calibracao_anatomica": (
                True
            ),

            "calibracao_corporal_pronta": (
                True
            ),

            "escala_visual_disponivel": (
                True
            ),

            "medidas_visuais_disponiveis": (
                True
            ),

            "geometria_consistente": (
                True
            ),

            "precisao_metrica_atual": (
                precisao_metrica
            ),

            "medidas_corrigidas": (
                False
            ),

            "mensagem": (
                "Os dados visuais passaram pelas "
                "validações necessárias para avançar "
                "à calibração anatômica."
            ),
        }

    motivos = []

    if not calibracao_pronta:
        motivos.append(
            "calibracao_corporal_nao_pronta"
        )

    if not escala_disponivel:
        motivos.append(
            "escala_visual_indisponivel"
        )

    if not medidas_calculadas:
        motivos.append(
            "medidas_visuais_indisponiveis"
        )

    if not geometria_consistente:
        motivos.append(
            "geometria_corporal_inconsistente"
        )

    return {
        "status": "dados_insuficientes",

        "pronta_para_calibracao_anatomica": (
            False
        ),

        "calibracao_corporal_pronta": (
            calibracao_pronta
        ),

        "escala_visual_disponivel": (
            escala_disponivel
        ),

        "medidas_visuais_disponiveis": (
            medidas_calculadas
        ),

        "geometria_consistente": (
            geometria_consistente
        ),

        "precisao_metrica_atual": (
            precisao_metrica
        ),

        "medidas_corrigidas": (
            False
        ),

        "motivos": (
            motivos
        ),

        "mensagem": (
            "Os dados atuais ainda não passaram "
            "por todas as validações necessárias "
            "para calibração anatômica."
        ),
    }


def avaliar_consistencia_geometrica(
    geometria_corporal,
    proporcoes_corporais,
    referencia_altura_corporal,
):
    """
    Avalia se a geometria corporal obtida
    apresenta relações internas coerentes.

    Esta função NÃO altera medidas e NÃO
    converte valores para centímetros.

    Ela verifica relações entre:
    - largura dos ombros
    - largura do quadril
    - altura corporal relativa
    - proporção ombros/quadril
    """

    if not geometria_corporal:
        return {
            "status": "geometria_indisponivel",
            "consistente": False,
            "motivos": [
                "geometria_corporal_ausente"
            ],
        }

    if not proporcoes_corporais:
        return {
            "status": (
                "proporcoes_indisponiveis"
            ),
            "consistente": False,
            "motivos": [
                "proporcoes_corporais_ausentes"
            ],
        }

    if not referencia_altura_corporal:
        return {
            "status": (
                "referencia_altura_indisponivel"
            ),
            "consistente": False,
            "motivos": [
                "referencia_altura_ausente"
            ],
        }

    largura_ombros = (
        geometria_corporal.get(
            "largura_ombros"
        )
    )

    largura_quadril = (
        geometria_corporal.get(
            "largura_quadril"
        )
    )

    proporcao_ombros_quadril = (
        proporcoes_corporais.get(
            "proporcao_ombros_quadril"
        )
    )

    altura_corpo_relativa = (
        referencia_altura_corporal.get(
            "altura_corpo_relativa"
        )
    )

    motivos = []

    # ======================================================
    # VALIDAÇÃO DOS DADOS
    # ======================================================

    if largura_ombros is None:
        motivos.append(
            "largura_ombros_indisponivel"
        )

    if largura_quadril is None:
        motivos.append(
            "largura_quadril_indisponivel"
        )

    if proporcao_ombros_quadril is None:
        motivos.append(
            "proporcao_ombros_quadril_indisponivel"
        )

    if altura_corpo_relativa is None:
        motivos.append(
            "altura_corpo_relativa_indisponivel"
        )

    if motivos:
        return {
            "status": (
                "dados_geometricos_incompletos"
            ),
            "consistente": False,
            "motivos": motivos,
        }

    # ======================================================
    # REFERÊNCIA VERTICAL
    # ======================================================

    if altura_corpo_relativa <= 0:
        return {
            "status": (
                "referencia_vertical_invalida"
            ),
            "consistente": False,
            "motivos": [
                "altura_corpo_relativa_invalida"
            ],
        }

    # ======================================================
    # RELAÇÕES GEOMÉTRICAS
    # ======================================================

    relacao_ombros_altura = (
        largura_ombros
        / altura_corpo_relativa
    )

    relacao_quadril_altura = (
        largura_quadril
        / altura_corpo_relativa
    )

    # ======================================================
    # CRITÉRIOS PROVISÓRIOS
    # ======================================================
    #
    # Os limites abaixo ainda NÃO representam
    # padrões antropométricos definitivos.
    #
    # Eles servem para rejeitar resultados
    # visuais claramente incompatíveis.
    # ======================================================

    ombros_validos = (
        0.10
        <= relacao_ombros_altura
        <= 0.60
    )

    quadril_valido = (
        0.08
        <= relacao_quadril_altura
        <= 0.50
    )

    proporcao_valida = (
        0.50
        <= proporcao_ombros_quadril
        <= 2.20
    )

    if not ombros_validos:
        motivos.append(
            "relacao_ombros_altura_fora_da_faixa"
        )

    if not quadril_valido:
        motivos.append(
            "relacao_quadril_altura_fora_da_faixa"
        )

    if not proporcao_valida:
        motivos.append(
            "proporcao_ombros_quadril_fora_da_faixa"
        )

    consistente = (
        ombros_validos
        and quadril_valido
        and proporcao_valida
    )

    if consistente:
        status = (
            "geometria_consistente"
        )

    else:
        status = (
            "geometria_com_ressalvas"
        )

    return {
        "status": (
            status
        ),

        "consistente": (
            consistente
        ),

        "relacao_ombros_altura": round(
            relacao_ombros_altura,
            4,
        ),

        "relacao_quadril_altura": round(
            relacao_quadril_altura,
            4,
        ),

        "proporcao_ombros_quadril": round(
            proporcao_ombros_quadril,
            4,
        ),

        "criterios": {
            "ombros_validos": (
                ombros_validos
            ),

            "quadril_valido": (
                quadril_valido
            ),

            "proporcao_valida": (
                proporcao_valida
            ),
        },

        "motivos": (
            motivos
        ),

        "mensagem": (
            "Consistência geométrica da imagem "
            "avaliada para futura calibração "
            "anatômica."
        ),
    }