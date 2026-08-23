def analisar_compatibilidade_dimensional(
    contexto_corpo_produto: dict,
    deteccao_humana: dict,
):
    """
    Camada de compatibilidade dimensional
    corpo x produto do VesteIA.

    Objetivos:
    - identificar medidas disponíveis;
    - liberar somente comparações semanticamente válidas;
    - registrar comparações ainda pendentes;
    - separar análise dimensional de recomendação final;
    - impedir recomendação definitiva quando as medidas
      ainda forem experimentais.

    Importante:
    largura de ombros corporal NÃO é tratada como
    equivalente à largura da camiseta.
    """

    # =========================================================
    # 1. VALIDAÇÃO DO CONTEXTO
    # =========================================================

    if not contexto_corpo_produto:
        return {
            "status": "dados_insuficientes",
            "categoria": None,
            "medidas_disponiveis": {},
            "comparacoes_liberadas": [],
            "comparacoes_pendentes": [],
            "alertas_semanticos": [],
            "comparacao_dimensional_completa": False,
            "nivel_decisao": "dados_insuficientes",
            "recomendacao_tamanho_liberada": False,
            "precisao": "experimental",
            "mensagem": (
                "Contexto corpo-produto indisponível "
                "para avaliação dimensional."
            ),
        }

    if not deteccao_humana:
        return {
            "status": "dados_insuficientes",
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
            "nivel_decisao": "dados_insuficientes",
            "recomendacao_tamanho_liberada": False,
            "precisao": "experimental",
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
        medidas_peca.get(
            "largura_cm"
        )
    )

    comprimento_peca_cm = (
        medidas_peca.get(
            "comprimento_cm"
        )
    )

    # =========================================================
    # 4. MEDIDAS CORPORAIS
    # =========================================================

    medidas_corporais = (
        deteccao_humana.get(
            "medidas_corporais_calibradas",
            {},
        )
    )

    largura_ombros_cm = (
        medidas_corporais.get(
            "largura_ombros_cm"
        )
    )

    largura_quadril_cm = (
        medidas_corporais.get(
            "largura_quadril_cm"
        )
    )

    largura_torax_cm = (
        medidas_corporais.get(
            "largura_torax_cm"
        )
    )

    comprimento_tronco_cm = (
        medidas_corporais.get(
            "comprimento_tronco_cm"
        )
    )

    comprimento_perna_cm = (
        medidas_corporais.get(
            "comprimento_perna_cm"
        )
    )

    comprimento_pe_cm = (
        medidas_corporais.get(
            "comprimento_pe_cm"
        )
    )

    largura_pe_cm = (
        medidas_corporais.get(
            "largura_pe_cm"
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
    # 5. GEOMETRIA RELATIVA
    # =========================================================

    geometria_corporal = (
        deteccao_humana.get(
            "geometria_corporal",
            {},
        )
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
    # 6. ESCALA CORPORAL
    # =========================================================

    escala_corporal = (
        deteccao_humana.get(
            "escala_corporal",
            {},
        )
    )

    escala_disponivel = (
        escala_corporal.get(
            "conversao_disponivel",
            False,
        )
    )

    # =========================================================
    # 7. MAPA DE DISPONIBILIDADE
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
    # 8. ESTRUTURAS DA ANÁLISE
    # =========================================================

    comparacoes_liberadas = []
    comparacoes_pendentes = []
    alertas_semanticos = []

    # =========================================================
    # 9. CAMISETA
    # =========================================================

    if categoria == "camiseta":

        if (
            largura_torax_cm is not None
            and largura_peca_cm is not None
        ):
            comparacoes_liberadas.append(
                "largura_torax_corpo_x_largura_peca"
            )
        else:
            comparacoes_pendentes.append(
                "largura_torax_corpo_x_largura_peca"
            )

        if (
            comprimento_tronco_cm is not None
            and comprimento_peca_cm is not None
        ):
            comparacoes_liberadas.append(
                "comprimento_tronco_x_comprimento_peca"
            )
        else:
            comparacoes_pendentes.append(
                "comprimento_tronco_x_comprimento_peca"
            )

        if (
            largura_ombros_cm is not None
            and largura_peca_cm is not None
        ):
            alertas_semanticos.append(
                (
                    "largura_ombros_cm não deve ser "
                    "comparada diretamente com "
                    "largura_cm da camiseta."
                )
            )

        if (
            origem_largura_torax
            == "estimativa_visual_interpolada"
        ):
            alertas_semanticos.append(
                (
                    "largura_torax_cm foi obtida por "
                    "estimativa visual interpolada e "
                    "não representa medida antropométrica "
                    "de precisão."
                )
            )

    # =========================================================
    # 10. CALÇA
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

    # =========================================================
    # 11. VESTIDO
    # =========================================================

    elif categoria == "vestido":

        if largura_torax_cm is None:
            comparacoes_pendentes.append(
                "largura_torax_corporal"
            )

        if largura_quadril_cm is None:
            comparacoes_pendentes.append(
                "largura_quadril_corporal"
            )

        if comprimento_tronco_cm is None:
            comparacoes_pendentes.append(
                "comprimento_tronco_corporal"
            )

        comparacoes_pendentes.extend(
            [
                "largura_torax_vestido",
                "largura_quadril_vestido",
                "comprimento_vestido",
            ]
        )

    # =========================================================
    # 12. CALÇADO
    # =========================================================

    elif categoria == "calcado":

        if comprimento_pe_cm is None:
            comparacoes_pendentes.append(
                "comprimento_pe_corporal"
            )

        if largura_pe_cm is None:
            comparacoes_pendentes.append(
                "largura_pe_corporal"
            )

        comparacoes_pendentes.extend(
            [
                "comprimento_interno_calcado",
                "largura_interna_calcado",
            ]
        )

    # =========================================================
    # 13. CATEGORIA NÃO MAPEADA
    # =========================================================

    else:
        comparacoes_pendentes.append(
            "categoria_sem_regras_dimensionais"
        )

    # =========================================================
    # 14. COMPLETUDE DIMENSIONAL
    # =========================================================

    comparacao_dimensional_completa = (
        len(comparacoes_pendentes) == 0
        and len(comparacoes_liberadas) > 0
    )

    # =========================================================
    # 15. CONFIANÇA DAS MEDIDAS
    # =========================================================

    medida_torax_experimental = (
        origem_largura_torax
        == "estimativa_visual_interpolada"
    )

    precisao_experimental = (
        precisao_medidas
        == "experimental"
    )

    medidas_apenas_experimentais = (
        medida_torax_experimental
        or precisao_experimental
        or not medidas_corrigidas_anatomicamente
    )

    # =========================================================
    # 16. LIBERAÇÃO DA RECOMENDAÇÃO FINAL
    # =========================================================

    recomendacao_tamanho_liberada = (
        comparacao_dimensional_completa
        and not medidas_apenas_experimentais
    )

    # =========================================================
    # 17. NÍVEL DE DECISÃO
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

    else:
        nivel_decisao = (
            "dados_parciais"
        )

    # =========================================================
    # 18. STATUS E MENSAGEM
    # =========================================================

    if comparacao_dimensional_completa:

        status = (
            "avaliacao_dimensional_completa"
        )

        if recomendacao_tamanho_liberada:
            mensagem = (
                "As comparações dimensionais necessárias "
                "estão disponíveis e passaram pelos "
                "critérios mínimos para recomendação."
            )

        else:
            mensagem = (
                "As comparações dimensionais necessárias "
                "estão disponíveis, mas a recomendação "
                "final de tamanho permanece bloqueada "
                "enquanto houver medidas experimentais "
                "ou não corrigidas anatomicamente."
            )

    else:

        status = (
            "avaliacao_dimensional_parcial"
        )

        mensagem = (
            "A análise dimensional foi preparada, "
            "mas ainda faltam medidas corporais ou "
            "medidas da peça semanticamente comparáveis."
        )

    # =========================================================
    # 19. CONTRATO DE SAÍDA
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

            "peca": {
                "largura_cm": (
                    largura_peca_cm
                ),
                "comprimento_cm": (
                    comprimento_peca_cm
                ),
            },
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

        "recomendacao_tamanho_liberada": (
            recomendacao_tamanho_liberada
        ),

        "precisao": "experimental",

        "mensagem": (
            mensagem
        ),
    }