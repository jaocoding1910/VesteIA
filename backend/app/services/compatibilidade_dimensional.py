def _valor_numerico(
    valor,
):
    """
    Converte um valor para float com segurança.

    Retorna None quando o valor não puder
    ser interpretado como número positivo.
    """

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


def analisar_compatibilidade_dimensional(
    contexto_corpo_produto: dict,
    deteccao_humana: dict,
):
    """
    Camada de compatibilidade dimensional
    corpo x produto do VesteIA.

    Responsabilidades:
    - identificar medidas disponíveis;
    - consumir a calibração específica de vestuário;
    - liberar somente comparações semanticamente válidas;
    - preservar métricas visuais como apoio e auditoria;
    - separar comparação experimental de recomendação final;
    - impedir que medidas visuais sejam tratadas
      como antropometria exata.

    Para camisetas:

    horizontal:
        largura_corporal_vestuario_cm
        x
        largura_cm da peça

    vertical:
        comprimento_corporal_vestuario_cm
        x
        comprimento_cm da peça

    IMPORTANTE:
    largura_torax_cm e largura_ombros_cm
    continuam disponíveis para rastreabilidade,
    mas NÃO são usadas diretamente como equivalentes
    à largura cadastrada da camiseta.
    """

    # =========================================================
    # 1. VALIDAÇÃO DO CONTEXTO
    # =========================================================

    if not contexto_corpo_produto:
        return {
            "status": (
                "dados_insuficientes"
            ),

            "categoria": None,

            "medidas_disponiveis": {},

            "comparacoes_liberadas": [],

            "comparacoes_pendentes": [],

            "alertas_semanticos": [],

            "comparacao_dimensional_completa": False,

            "nivel_decisao": (
                "dados_insuficientes"
            ),

            "recomendacao_tamanho_liberada": False,

            "precisao": (
                "experimental"
            ),

            "mensagem": (
                "Contexto corpo-produto indisponível "
                "para avaliação dimensional."
            ),
        }

    if not deteccao_humana:
        return {
            "status": (
                "dados_insuficientes"
            ),

            "categoria": (
                contexto_corpo_produto.get(
                    "categoria"
                )
            ),

            "medidas_disponiveis": {},

            "comparacoes_liberadas": [],

            "comparacoes_pendentes": [],

            "alertas_semanticos": [],

            "comparacao_dimensional_completa": False,

            "nivel_decisao": (
                "dados_insuficientes"
            ),

            "recomendacao_tamanho_liberada": False,

            "precisao": (
                "experimental"
            ),

            "mensagem": (
                "Dados corporais indisponíveis "
                "para avaliação dimensional."
            ),
        }

    # =========================================================
    # 2. CATEGORIA
    # =========================================================

    categoria = (
        contexto_corpo_produto.get(
            "categoria"
        )
    )

    if categoria:
        categoria = (
            str(
                categoria
            )
            .strip()
            .lower()
        )

    # =========================================================
    # 3. MEDIDAS DA PEÇA
    # =========================================================

    medidas_peca = (
        contexto_corpo_produto.get(
            "medidas_peca",
            {},
        )
    )

    largura_peca_cm = (
        _valor_numerico(
            medidas_peca.get(
                "largura_cm"
            )
        )
    )

    comprimento_peca_cm = (
        _valor_numerico(
            medidas_peca.get(
                "comprimento_cm"
            )
        )
    )

    # =========================================================
    # 4. MEDIDAS CORPORAIS VISUAIS / CALIBRADAS
    # =========================================================

    medidas_corporais = (
        deteccao_humana.get(
            "medidas_corporais_calibradas",
            {},
        )
        or {}
    )

    largura_ombros_cm = (
        _valor_numerico(
            medidas_corporais.get(
                "largura_ombros_cm"
            )
        )
    )

    largura_quadril_cm = (
        _valor_numerico(
            medidas_corporais.get(
                "largura_quadril_cm"
            )
        )
    )

    largura_torax_cm = (
        _valor_numerico(
            medidas_corporais.get(
                "largura_torax_cm"
            )
        )
    )

    comprimento_tronco_cm = (
        _valor_numerico(
            medidas_corporais.get(
                "comprimento_tronco_cm"
            )
        )
    )

    comprimento_perna_cm = (
        _valor_numerico(
            medidas_corporais.get(
                "comprimento_perna_cm"
            )
        )
    )

    comprimento_pe_cm = (
        _valor_numerico(
            medidas_corporais.get(
                "comprimento_pe_cm"
            )
        )
    )

    largura_pe_cm = (
        _valor_numerico(
            medidas_corporais.get(
                "largura_pe_cm"
            )
        )
    )

    origem_largura_torax = (
        medidas_corporais.get(
            "origem_largura_torax"
        )
    )

    precisao_medidas = (
        medidas_corporais.get(
            "precisao"
        )
    )

    medidas_corrigidas_anatomicamente = (
        medidas_corporais.get(
            "medidas_corrigidas_anatomicamente",
            False,
        )
    )

    # =========================================================
    # 5. CALIBRAÇÃO DE VESTUÁRIO
    # =========================================================

    calibracao_vestuario = (
        deteccao_humana.get(
            "calibracao_vestuario",
            {},
        )
        or {}
    )

    calibracao_vestuario_disponivel = (
        calibracao_vestuario.get(
            "calibracao_disponivel",
            False,
        )
    )

    comparacao_horizontal_disponivel = (
        calibracao_vestuario.get(
            "comparacao_horizontal_disponivel",
            False,
        )
    )

    comparacao_vertical_disponivel = (
        calibracao_vestuario.get(
            "comparacao_vertical_disponivel",
            False,
        )
    )

    largura_corporal_vestuario_cm = (
        _valor_numerico(
            calibracao_vestuario.get(
                "largura_corporal_vestuario_cm"
            )
        )
    )

    comprimento_corporal_vestuario_cm = (
        _valor_numerico(
            calibracao_vestuario.get(
                "comprimento_corporal_vestuario_cm"
            )
        )
    )

    qualidade_calibracao_vestuario = (
        calibracao_vestuario.get(
            "qualidade",
            {},
        )
        or {}
    )

    nivel_qualidade_calibracao = (
        qualidade_calibracao_vestuario.get(
            "nivel",
            "indisponivel",
        )
    )

    pontuacao_qualidade_calibracao = (
        qualidade_calibracao_vestuario.get(
            "pontuacao",
            0,
        )
    )

    calibracao_vestuario_experimental = (
        calibracao_vestuario.get(
            "experimental",
            True,
        )
    )

    # =========================================================
    # 6. LARGURA CORPORAL EQUIVALENTE
    # =========================================================

    largura_corporal_equivalente = (
        deteccao_humana.get(
            "largura_corporal_equivalente",
            {},
        )
        or {}
    )

    largura_equivalente_disponivel = (
        largura_corporal_equivalente.get(
            "disponivel",
            False,
        )
    )

    largura_equivalente_cm = (
        _valor_numerico(
            largura_corporal_equivalente.get(
                "largura_corporal_equivalente_cm"
            )
        )
    )

    # =========================================================
    # 7. GEOMETRIA RELATIVA
    # =========================================================

    geometria_corporal = (
        deteccao_humana.get(
            "geometria_corporal",
            {},
        )
        or {}
    )

    largura_ombros_relativa = (
        geometria_corporal.get(
            "largura_ombros"
        )
    )

    largura_quadril_relativa = (
        geometria_corporal.get(
            "largura_quadril"
        )
    )

    largura_torax_relativa = (
        geometria_corporal.get(
            "largura_torax_relativa"
        )
    )

    comprimento_tronco_relativo = (
        geometria_corporal.get(
            "comprimento_tronco_relativo"
        )
    )

    # =========================================================
    # 8. ESCALA CORPORAL
    # =========================================================

    escala_corporal = (
        deteccao_humana.get(
            "escala_corporal",
            {},
        )
        or {}
    )

    escala_disponivel = (
        escala_corporal.get(
            "conversao_disponivel",
            False,
        )
    )

    # =========================================================
    # 9. CONFIANÇA MÉTRICA
    # =========================================================

    confianca_metrica = (
        deteccao_humana.get(
            "confianca_metrica",
            {},
        )
        or {}
    )

    nivel_confianca_metrica = (
        confianca_metrica.get(
            "nivel",
            "indisponivel",
        )
    )

    pontuacao_confianca_metrica = (
        confianca_metrica.get(
            "pontuacao",
            0,
        )
    )

    # =========================================================
    # 10. MAPA DE DISPONIBILIDADE
    # =========================================================

    medidas_disponiveis = {
        "ombros_cm": (
            largura_ombros_cm
            is not None
        ),

        "quadril_cm": (
            largura_quadril_cm
            is not None
        ),

        "largura_torax_cm": (
            largura_torax_cm
            is not None
        ),

        "comprimento_tronco_cm": (
            comprimento_tronco_cm
            is not None
        ),

        "comprimento_perna_cm": (
            comprimento_perna_cm
            is not None
        ),

        "comprimento_pe_cm": (
            comprimento_pe_cm
            is not None
        ),

        "largura_pe_cm": (
            largura_pe_cm
            is not None
        ),

        "ombros_relativos": (
            largura_ombros_relativa
            is not None
        ),

        "quadril_relativos": (
            largura_quadril_relativa
            is not None
        ),

        "largura_torax_relativa": (
            largura_torax_relativa
            is not None
        ),

        "comprimento_tronco_relativo": (
            comprimento_tronco_relativo
            is not None
        ),

        "escala_corporal": (
            escala_disponivel
        ),

        # -----------------------------------------------------
        # NOVA CAMADA
        # -----------------------------------------------------

        "calibracao_vestuario": (
            calibracao_vestuario_disponivel
        ),

        "largura_corporal_equivalente_cm": (
            largura_equivalente_disponivel
            and largura_equivalente_cm
            is not None
        ),

        "largura_corporal_vestuario_cm": (
            comparacao_horizontal_disponivel
            and largura_corporal_vestuario_cm
            is not None
        ),

        "comprimento_corporal_vestuario_cm": (
            comparacao_vertical_disponivel
            and comprimento_corporal_vestuario_cm
            is not None
        ),

        "largura_peca_cm": (
            largura_peca_cm
            is not None
        ),

        "comprimento_peca_cm": (
            comprimento_peca_cm
            is not None
        ),
    }

    # =========================================================
    # 11. ESTRUTURAS DA ANÁLISE
    # =========================================================

    comparacoes_liberadas = []

    comparacoes_pendentes = []

    alertas_semanticos = []

    # =========================================================
    # 12. CAMISETA
    # =========================================================

    if categoria == "camiseta":

        # -----------------------------------------------------
        # HORIZONTAL
        # -----------------------------------------------------
        #
        # A comparação agora usa EXCLUSIVAMENTE
        # a referência gerada pela calibração de vestuário.
        #
        # largura_torax_cm e largura_ombros_cm
        # continuam apenas como métricas de origem.
        # -----------------------------------------------------

        horizontal_valida = (
            comparacao_horizontal_disponivel
            and largura_corporal_vestuario_cm
            is not None
            and largura_peca_cm
            is not None
        )

        if horizontal_valida:

            comparacoes_liberadas.append(
                "largura_corporal_vestuario_x_largura_peca"
            )

        else:

            comparacoes_pendentes.append(
                "largura_corporal_vestuario_x_largura_peca"
            )

        # -----------------------------------------------------
        # VERTICAL
        # -----------------------------------------------------

        vertical_valida = (
            comparacao_vertical_disponivel
            and comprimento_corporal_vestuario_cm
            is not None
            and comprimento_peca_cm
            is not None
        )

        if vertical_valida:

            comparacoes_liberadas.append(
                "comprimento_corporal_vestuario_x_comprimento_peca"
            )

        else:

            comparacoes_pendentes.append(
                "comprimento_corporal_vestuario_x_comprimento_peca"
            )

        # -----------------------------------------------------
        # ALERTAS SEMÂNTICOS
        # -----------------------------------------------------

        if largura_torax_cm is not None:

            alertas_semanticos.append(
                (
                    "largura_torax_cm permanece disponível "
                    "como projeção visual do tórax, mas não "
                    "é utilizada diretamente como equivalente "
                    "à largura_cm da camiseta."
                )
            )

        if largura_ombros_cm is not None:

            alertas_semanticos.append(
                (
                    "largura_ombros_cm permanece disponível "
                    "para análise proporcional, mas não é "
                    "comparada diretamente com largura_cm "
                    "da camiseta."
                )
            )

        if (
            origem_largura_torax
            == "estimativa_visual_interpolada"
        ):

            alertas_semanticos.append(
                (
                    "A projeção visual do tórax participa "
                    "indiretamente da construção da referência "
                    "horizontal de vestuário, sem ser tratada "
                    "como medida antropométrica exata."
                )
            )

        if horizontal_valida:

            alertas_semanticos.append(
                (
                    "A comparação horizontal utiliza "
                    "largura_corporal_vestuario_cm, uma "
                    "referência derivada experimental do "
                    "motor de vestuário."
                )
            )

        if vertical_valida:

            alertas_semanticos.append(
                (
                    "A comparação vertical utiliza "
                    "comprimento_corporal_vestuario_cm "
                    "como referência corporal experimental."
                )
            )

    # =========================================================
    # 13. CALÇA
    # =========================================================

    elif categoria == "calca":

        if largura_quadril_cm is not None:

            comparacoes_liberadas.append(
                "largura_quadril_corporal_disponivel"
            )

        else:

            comparacoes_pendentes.append(
                "largura_quadril_corporal"
            )

        if comprimento_perna_cm is not None:

            comparacoes_liberadas.append(
                "comprimento_perna_corporal_disponivel"
            )

        else:

            comparacoes_pendentes.append(
                "comprimento_perna_corporal"
            )

        comparacoes_pendentes.extend(
            [
                "largura_quadril_peca",
                "comprimento_calca",
            ]
        )

        alertas_semanticos.append(
            (
                "A calibração de vestuário atual foi "
                "estruturada inicialmente para comparação "
                "horizontal e vertical do tronco. Calças "
                "ainda exigem métricas próprias de quadril "
                "e comprimento da peça."
            )
        )

    # =========================================================
    # 14. VESTIDO
    # =========================================================

    elif categoria == "vestido":

        if (
            comparacao_horizontal_disponivel
            and largura_corporal_vestuario_cm
            is not None
        ):

            comparacoes_liberadas.append(
                "referencia_horizontal_tronco_disponivel"
            )

        else:

            comparacoes_pendentes.append(
                "referencia_horizontal_tronco"
            )

        if largura_quadril_cm is None:

            comparacoes_pendentes.append(
                "largura_quadril_corporal"
            )

        if (
            comparacao_vertical_disponivel
            and comprimento_corporal_vestuario_cm
            is not None
        ):

            comparacoes_liberadas.append(
                "referencia_vertical_tronco_disponivel"
            )

        else:

            comparacoes_pendentes.append(
                "referencia_vertical_tronco"
            )

        comparacoes_pendentes.extend(
            [
                "largura_torax_vestido",
                "largura_quadril_vestido",
                "comprimento_vestido",
            ]
        )

    # =========================================================
    # 15. CALÇADO
    # =========================================================

    elif categoria == "calcado":

        if comprimento_pe_cm is None:

            comparacoes_pendentes.append(
                "comprimento_pe_corporal"
            )

        else:

            comparacoes_liberadas.append(
                "comprimento_pe_corporal_disponivel"
            )

        if largura_pe_cm is None:

            comparacoes_pendentes.append(
                "largura_pe_corporal"
            )

        else:

            comparacoes_liberadas.append(
                "largura_pe_corporal_disponivel"
            )

        comparacoes_pendentes.extend(
            [
                "comprimento_interno_calcado",
                "largura_interna_calcado",
            ]
        )

    # =========================================================
    # 16. CATEGORIA NÃO MAPEADA
    # =========================================================

    else:

        comparacoes_pendentes.append(
            "categoria_sem_regras_dimensionais"
        )

    # =========================================================
    # 17. COMPLETUDE DIMENSIONAL
    # =========================================================

    comparacao_dimensional_completa = (
        len(
            comparacoes_pendentes
        )
        == 0
        and len(
            comparacoes_liberadas
        )
        > 0
    )

    # =========================================================
    # 18. NATUREZA EXPERIMENTAL
    # =========================================================

    medida_torax_experimental = (
        origem_largura_torax
        == "estimativa_visual_interpolada"
    )

    precisao_experimental = (
        precisao_medidas
        == "experimental"
    )

    largura_equivalente_experimental = (
        largura_corporal_equivalente.get(
            "experimental",
            True,
        )
    )

    medidas_apenas_experimentais = (
        medida_torax_experimental
        or precisao_experimental
        or calibracao_vestuario_experimental
        or largura_equivalente_experimental
        or not medidas_corrigidas_anatomicamente
    )

    # =========================================================
    # 19. QUALIDADE DA CALIBRAÇÃO
    # =========================================================

    qualidade_calibracao_suficiente = (
        nivel_qualidade_calibracao
        in (
            "alta",
            "media",
        )
    )

    confianca_metrica_suficiente = (
        nivel_confianca_metrica
        in (
            "alta",
            "media",
        )
    )

    # =========================================================
    # 20. RECOMENDAÇÃO DEFINITIVA
    # =========================================================
    #
    # Mesmo com horizontal + vertical disponíveis,
    # a recomendação definitiva permanece bloqueada
    # enquanto a referência corporal for experimental.
    #
    # O motor poderá gerar sugestão/ranking experimental.
    # =========================================================

    recomendacao_tamanho_liberada = (
        comparacao_dimensional_completa
        and qualidade_calibracao_suficiente
        and confianca_metrica_suficiente
        and not medidas_apenas_experimentais
    )

    # =========================================================
    # 21. NÍVEL DE DECISÃO
    # =========================================================

    if comparacao_dimensional_completa:

        if recomendacao_tamanho_liberada:

            nivel_decisao = (
                "recomendacao_dimensional_liberada"
            )

        else:

            nivel_decisao = (
                "sugestao_experimental"
            )

    elif comparacoes_liberadas:

        nivel_decisao = (
            "dados_parciais"
        )

    else:

        nivel_decisao = (
            "dados_insuficientes"
        )

    # =========================================================
    # 22. STATUS / MENSAGEM
    # =========================================================

    if comparacao_dimensional_completa:

        status = (
            "avaliacao_dimensional_completa"
        )

        if recomendacao_tamanho_liberada:

            mensagem = (
                "As comparações dimensionais necessárias "
                "estão disponíveis e passaram pelos "
                "critérios definidos para recomendação."
            )

        else:

            mensagem = (
                "As comparações horizontal e vertical "
                "necessárias estão disponíveis por meio "
                "da calibração de vestuário. O motor pode "
                "produzir uma sugestão experimental de "
                "tamanho, mas a recomendação definitiva "
                "permanece bloqueada enquanto as referências "
                "corporais ainda forem experimentais."
            )

    elif comparacoes_liberadas:

        status = (
            "avaliacao_dimensional_parcial"
        )

        mensagem = (
            "Parte das comparações dimensionais está "
            "disponível, mas ainda existem dimensões "
            "pendentes para uma análise completa."
        )

    else:

        status = (
            "avaliacao_dimensional_insuficiente"
        )

        mensagem = (
            "Não existem comparações dimensionais "
            "semanticamente suficientes para continuar."
        )

    # =========================================================
    # 23. CONTRATO FINAL
    # =========================================================

    return {
        "status": (
            status
        ),

        "categoria": (
            categoria
        ),

        "medidas_disponiveis": (
            medidas_disponiveis
        ),

        "medidas_referencia": {
            # -------------------------------------------------
            # VALORES ORIGINAIS
            # -------------------------------------------------

            "corpo": {
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

                "comprimento_perna_cm": (
                    comprimento_perna_cm
                ),

                "comprimento_pe_cm": (
                    comprimento_pe_cm
                ),

                "largura_pe_cm": (
                    largura_pe_cm
                ),

                "largura_ombros_relativa": (
                    largura_ombros_relativa
                ),

                "largura_quadril_relativa": (
                    largura_quadril_relativa
                ),

                "largura_torax_relativa": (
                    largura_torax_relativa
                ),

                "comprimento_tronco_relativo": (
                    comprimento_tronco_relativo
                ),
            },

            # -------------------------------------------------
            # REFERÊNCIAS OFICIAIS DO MOTOR DE VESTUÁRIO
            # -------------------------------------------------

            "vestuario": {
                "largura_corporal_vestuario_cm": (
                    largura_corporal_vestuario_cm
                ),

                "comprimento_corporal_vestuario_cm": (
                    comprimento_corporal_vestuario_cm
                ),

                "largura_corporal_equivalente_cm": (
                    largura_equivalente_cm
                ),

                "comparacao_horizontal_disponivel": (
                    comparacao_horizontal_disponivel
                ),

                "comparacao_vertical_disponivel": (
                    comparacao_vertical_disponivel
                ),
            },

            "peca": {
                "largura_cm": (
                    largura_peca_cm
                ),

                "comprimento_cm": (
                    comprimento_peca_cm
                ),
            },
        },

        "calibracao_vestuario": {
            "status": (
                calibracao_vestuario.get(
                    "status"
                )
            ),

            "disponivel": (
                calibracao_vestuario_disponivel
            ),

            "comparacao_horizontal_disponivel": (
                comparacao_horizontal_disponivel
            ),

            "comparacao_vertical_disponivel": (
                comparacao_vertical_disponivel
            ),

            "qualidade": {
                "nivel": (
                    nivel_qualidade_calibracao
                ),

                "pontuacao": (
                    pontuacao_qualidade_calibracao
                ),
            },

            "experimental": (
                calibracao_vestuario_experimental
            ),

            "versao": (
                calibracao_vestuario.get(
                    "versao_calibracao"
                )
            ),
        },

        "confianca_metrica": {
            "nivel": (
                nivel_confianca_metrica
            ),

            "pontuacao": (
                pontuacao_confianca_metrica
            ),
        },

        "origem_medidas": {
            "largura_torax": (
                origem_largura_torax
            ),

            "precisao_corporal": (
                precisao_medidas
            ),

            "medidas_corrigidas_anatomicamente": (
                medidas_corrigidas_anatomicamente
            ),

            "largura_horizontal_motor": (
                "calibracao_vestuario."
                "largura_corporal_vestuario_cm"
            ),

            "comprimento_vertical_motor": (
                "calibracao_vestuario."
                "comprimento_corporal_vestuario_cm"
            ),
        },

        "comparacoes_liberadas": (
            comparacoes_liberadas
        ),

        "comparacoes_pendentes": (
            comparacoes_pendentes
        ),

        "alertas_semanticos": (
            alertas_semanticos
        ),

        "comparacao_dimensional_completa": (
            comparacao_dimensional_completa
        ),

        "nivel_decisao": (
            nivel_decisao
        ),

        "medidas_apenas_experimentais": (
            medidas_apenas_experimentais
        ),

        "qualidade_calibracao_suficiente": (
            qualidade_calibracao_suficiente
        ),

        "confianca_metrica_suficiente": (
            confianca_metrica_suficiente
        ),

        "recomendacao_tamanho_liberada": (
            recomendacao_tamanho_liberada
        ),

        "sugestao_experimental_liberada": (
            comparacao_dimensional_completa
            and qualidade_calibracao_suficiente
            and confianca_metrica_suficiente
        ),

        "precisao": (
            "experimental"
        ),

        "mensagem": (
            mensagem
        ),
    }