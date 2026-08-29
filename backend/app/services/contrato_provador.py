from app.services.candidatos_referencia_corporal import (
    gerar_candidatos_altura_referencia,
)


def gerar_contrato_provador_v1(
    sessao_id: int,
    produto: dict,
    variacoes_produto: list,
    decisao_provador: dict,
    recomendacao_tamanho_provador: dict,
    deteccao: dict,
    preferencia_caimento: str,
):
    """
    Gera o contrato enxuto do Provador VesteIA V1.

    Esta camada existe para consumo do:
    - frontend;
    - futura camada de Avatar;
    - integrações externas.

    IMPORTANTE:
    Esta função NÃO recalcula:
    - calibração;
    - métricas corporais;
    - compatibilidade;
    - ranking;
    - scores;
    - recomendação.

    Ela apenas transforma resultados já calculados
    pelo pipeline em um contrato estável e amigável.

    Sprint 49:
    - contrato Provador V1;
    - origem corporal explícita;
    - referência corporal explícita;
    - preparação para seleção visual de Avatar;
    - geração de candidatos de altura de referência;
    - preparação para futura entrada manual;
    - nenhuma geração de Avatar nesta etapa.
    """

    produto = produto or {}
    variacoes_produto = (
        variacoes_produto
        or []
    )
    decisao_provador = (
        decisao_provador
        or {}
    )
    recomendacao_tamanho_provador = (
        recomendacao_tamanho_provador
        or {}
    )
    deteccao = (
        deteccao
        or {}
    )

    # ======================================================
    # ESTADO GERAL
    # ======================================================

    pode_continuar = bool(
        decisao_provador.get(
            "pode_continuar",
            False,
        )
    )

    status_decisao = (
        decisao_provador.get(
            "status",
            "indisponivel",
        )
    )

    if not pode_continuar:
        status_contrato = (
            "nova_foto_necessaria"
        )

    elif (
        status_decisao
        == "analise_consolidada"
    ):
        status_contrato = (
            "analise_concluida"
        )

    else:
        status_contrato = (
            "analise_indisponivel"
        )

    # ======================================================
    # ORIGEM DA ANÁLISE
    # ======================================================

    origem_analise = (
        decisao_provador.get(
            "origem_analise"
        )
        or {}
    )

    tipo_origem = (
        origem_analise.get(
            "tipo"
        )
        or "foto"
    )

    origens_corporais_suportadas = [
        "foto",
        "selecao_visual_avatar",
        "manual",
    ]

    if (
        tipo_origem
        not in origens_corporais_suportadas
    ):
        tipo_origem = "foto"

    origem_corporal = {
        "tipo": (
            tipo_origem
        ),

        "origens_suportadas": (
            origens_corporais_suportadas
        ),

        "usa_visao_computacional": bool(
            origem_analise.get(
                "usa_visao_computacional",
                tipo_origem == "foto",
            )
        ),

        "usa_calibracao_corporal": bool(
            origem_analise.get(
                "usa_calibracao_corporal",
                tipo_origem == "foto",
            )
        ),

        "selecionada_pelo_usuario": (
            tipo_origem
            == "selecao_visual_avatar"
        ),

        "entrada_manual": (
            tipo_origem
            == "manual"
        ),

        "experimental": True,
    }

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recomendacao = (
        decisao_provador.get(
            "recomendacao_tamanho"
        )
        or {}
    )

    tamanho_sugerido = (
        recomendacao.get(
            "tamanho"
        )
    )

    tamanho_alternativo = (
        recomendacao.get(
            "tamanho_alternativo"
        )
    )

    ranking = (
        recomendacao.get(
            "ranking"
        )
        or recomendacao_tamanho_provador.get(
            "ranking"
        )
        or []
    )

    # ======================================================
    # RANKING ENXUTO PARA FRONTEND
    # ======================================================

    tamanhos = []

    for item in ranking:
        if not isinstance(
            item,
            dict,
        ):
            continue

        tamanhos.append(
            {
                "produto_id": (
                    item.get(
                        "produto_id"
                    )
                ),

                "tamanho": (
                    item.get(
                        "tamanho"
                    )
                ),

                "posicao": (
                    item.get(
                        "posicao"
                    )
                ),

                "pontuacao": (
                    item.get(
                        "pontuacao"
                    )
                ),

                "caimento_largura": (
                    item.get(
                        "caimento_largura"
                    )
                ),

                "caimento_comprimento": (
                    item.get(
                        "caimento_comprimento"
                    )
                ),

                "resultado": (
                    item.get(
                        "resultado"
                    )
                ),
            }
        )

    # ======================================================
    # VARIAÇÕES DISPONÍVEIS
    # ======================================================

    variacoes = []

    for variacao in variacoes_produto:
        if not isinstance(
            variacao,
            dict,
        ):
            continue

        variacoes.append(
            {
                "id": (
                    variacao.get(
                        "id"
                    )
                ),

                "tamanho": (
                    variacao.get(
                        "tamanho"
                    )
                ),

                "largura_cm": (
                    variacao.get(
                        "largura_cm"
                    )
                ),

                "comprimento_cm": (
                    variacao.get(
                        "comprimento_cm"
                    )
                ),
            }
        )

    tamanhos_disponiveis = [
        item.get(
            "tamanho"
        )
        for item in variacoes
        if item.get(
            "tamanho"
        )
    ]

    # ======================================================
    # CONFIANÇA DA RECOMENDAÇÃO
    # ======================================================

    confianca_ranking = (
        recomendacao.get(
            "confianca_ranking"
        )
        or {}
    )

    zona_decisao = (
        recomendacao.get(
            "zona_decisao"
        )
        or {}
    )

    # ======================================================
    # REFERÊNCIA CORPORAL
    # ======================================================

    calibracao_corporal = (
        deteccao.get(
            "calibracao_corporal"
        )
        or {}
    )

    altura_referencia_cm = (
        calibracao_corporal.get(
            "altura_cm"
        )
    )

    if (
        tipo_origem == "foto"
        and altura_referencia_cm
        is not None
    ):
        origem_altura = (
            "perfil_usuario"
        )

    elif (
        tipo_origem
        == "selecao_visual_avatar"
    ):
        origem_altura = (
            "selecao_visual_avatar"
        )

    elif (
        tipo_origem
        == "manual"
    ):
        origem_altura = (
            "entrada_manual"
        )

    else:
        origem_altura = (
            "indisponivel"
        )

    confianca_metrica = (
        deteccao.get(
            "confianca_metrica"
        )
        or {}
    )

    calibracao_vestuario = (
        deteccao.get(
            "calibracao_vestuario"
        )
        or {}
    )

    referencias_vestuario = (
        calibracao_vestuario.get(
            "referencias_vestuario"
        )
        or {}
    )

    largura_corporal_vestuario_cm = (
        referencias_vestuario.get(
            "largura_corporal_vestuario_cm"
        )
    )

    comprimento_corporal_vestuario_cm = (
        referencias_vestuario.get(
            "comprimento_corporal_vestuario_cm"
        )
    )

    referencia_corporal_disponivel = bool(
        altura_referencia_cm
        is not None
        or largura_corporal_vestuario_cm
        is not None
        or comprimento_corporal_vestuario_cm
        is not None
    )

    referencia_corporal = {
        "disponivel": (
            referencia_corporal_disponivel
        ),

        "origem_corporal": (
            tipo_origem
        ),

        "altura_referencia_cm": (
            altura_referencia_cm
        ),

        "origem_altura": (
            origem_altura
        ),

        "altura_confirmada_pelo_usuario": (
            False
        ),

        "largura_corporal_vestuario_cm": (
            largura_corporal_vestuario_cm
        ),

        "comprimento_corporal_vestuario_cm": (
            comprimento_corporal_vestuario_cm
        ),

        "confianca_metrica": (
            confianca_metrica.get(
                "nivel"
            )
        ),

        "pontuacao_confianca_metrica": (
            confianca_metrica.get(
                "pontuacao"
            )
        ),

        "experimental": (
            True
        ),

        "altura_anatomica_exata": (
            False
        ),

        "mensagem": (
            "A referência corporal representa "
            "os dados utilizados pelo motor "
            "do VesteIA e não deve ser "
            "interpretada como medição "
            "antropométrica exata."
        ),
    }

    # ======================================================
    # CANDIDATOS DE ALTURA DE REFERÊNCIA
    # ======================================================
    #
    # Aqui NÃO estamos estimando a altura real.
    #
    # Apenas criamos referências próximas
    # ao valor central para futura comparação
    # visual no Avatar.
    #
    # Sprint 49:
    # quantidade fixa e previsível para o MVP.
    #
    # Futuramente a quantidade poderá variar
    # conforme confiança/incerteza do motor.
    # ======================================================

    candidatos_altura = (
        gerar_candidatos_altura_referencia(
            altura_central_cm=(
                altura_referencia_cm
            ),
            quantidade=4,
            intervalo_cm=3,
        )
    )

    # ======================================================
    # SELEÇÃO VISUAL DE ALTURA
    # ======================================================

    selecao_visual_altura = {
        "suportada_no_contrato": (
            True
        ),

        "ativa": (
            tipo_origem
            == "selecao_visual_avatar"
        ),

        "obrigatoria": (
            False
        ),

        "altura_central_referencia_cm": (
            altura_referencia_cm
        ),

        "altura_selecionada_cm": (
            None
        ),

        "usuario_confirmou_referencia": (
            False
        ),

        "origem_selecao": (
            "selecao_visual_avatar"
        ),

        "candidatos": (
            candidatos_altura.get(
                "candidatos",
                [],
            )
        ),

        "geracao_candidatos_implementada": (
            candidatos_altura.get(
                "disponivel",
                False,
            )
        ),

        "quantidade_candidatos": (
            candidatos_altura.get(
                "quantidade",
                0,
            )
        ),

        "intervalo_candidatos_cm": (
            candidatos_altura.get(
                "intervalo_cm"
            )
        ),

        "permite_incerteza_usuario": (
            True
        ),

        "opcao_nao_tenho_certeza": (
            True
        ),

        "altura_anatomica_exata": (
            False
        ),

        "experimental": (
            True
        ),
    }

    # ======================================================
    # AVATAR — PREPARAÇÃO
    # ======================================================

    avatar_preparavel = bool(
        pode_continuar
        and origem_analise.get(
            "avatar_preparavel",
            False,
        )
    )

    avatar = {
        "preparavel": (
            avatar_preparavel
        ),

        "gerado": (
            False
        ),

        "status": (
            "preparado_para_futura_geracao"
            if avatar_preparavel
            else "indisponivel"
        ),

        "origem_corporal": (
            tipo_origem
        ),

        "referencia_corporal": (
            referencia_corporal
        ),

        "produto": {
            "id": (
                produto.get(
                    "id"
                )
            ),

            "modelagem": (
                produto.get(
                    "modelagem"
                )
            ),

            "tamanho_recomendado": (
                tamanho_sugerido
            ),

            "tamanho_alternativo": (
                tamanho_alternativo
            ),

            "tamanhos_disponiveis": (
                tamanhos_disponiveis
            ),
        },

        "selecao_visual_altura": (
            selecao_visual_altura
        ),
    }

    # ======================================================
    # CONTRATO FINAL
    # ======================================================

    return {
        "versao_contrato": (
            "provador_v1"
        ),

        "sessao_id": (
            sessao_id
        ),

        "status": (
            status_contrato
        ),

        "pode_continuar": (
            pode_continuar
        ),

        "produto": {
            "id": (
                produto.get(
                    "id"
                )
            ),

            "nome": (
                produto.get(
                    "nome"
                )
            ),

            "categoria": (
                produto.get(
                    "categoria"
                )
            ),

            "cor": (
                produto.get(
                    "cor"
                )
            ),

            "modelagem": (
                produto.get(
                    "modelagem"
                )
            ),
        },

        "analise": {
            "origem": (
                tipo_origem
            ),

            "origem_corporal": (
                origem_corporal
            ),

            "qualidade_foto": (
                decisao_provador.get(
                    "qualidade_foto"
                )
            ),

            "confianca_visual": (
                decisao_provador.get(
                    "confianca_visual"
                )
            ),

            "comparacao_dimensional_completa": (
                decisao_provador.get(
                    "comparacao_dimensional_completa",
                    False,
                )
            ),

            "experimental": (
                True
            ),
        },

        "recomendacao": {
            "disponivel": (
                recomendacao.get(
                    "disponivel",
                    False,
                )
            ),

            "sugestao_liberada": (
                recomendacao.get(
                    "sugestao_liberada",
                    False,
                )
            ),

            "recomendacao_definitiva_liberada": (
                recomendacao.get(
                    "recomendacao_definitiva_liberada",
                    False,
                )
            ),

            "tamanho": (
                tamanho_sugerido
            ),

            "tamanho_alternativo": (
                tamanho_alternativo
            ),

            "pontuacao": (
                recomendacao.get(
                    "pontuacao"
                )
            ),

            "preferencia_caimento": (
                preferencia_caimento
            ),

            "modelagem": (
                recomendacao.get(
                    "modelagem"
                )
                or produto.get(
                    "modelagem"
                )
            ),

            "empate_tecnico": (
                recomendacao.get(
                    "empate_tecnico",
                    False,
                )
            ),

            "alternativa_forte": (
                recomendacao.get(
                    "alternativa_forte",
                    False,
                )
            ),

            "decisao_unica": (
                recomendacao.get(
                    "decisao_unica",
                    False,
                )
            ),

            "status": (
                recomendacao.get(
                    "status"
                )
            ),

            "nivel": (
                recomendacao.get(
                    "nivel"
                )
            ),

            "confianca": {
                "nivel": (
                    confianca_ranking.get(
                        "nivel"
                    )
                ),

                "diferenca_primeiro_segundo": (
                    confianca_ranking.get(
                        "diferenca_primeiro_segundo"
                    )
                ),
            },

            "zona_decisao": {
                "status": (
                    zona_decisao.get(
                        "status"
                    )
                ),

                "diferenca": (
                    zona_decisao.get(
                        "diferenca"
                    )
                ),
            },
        },

        "caimento": {
            "resultado": (
                decisao_provador.get(
                    "resultado_caimento"
                )
            ),

            "destaques": (
                decisao_provador.get(
                    "destaques"
                )
                or []
            ),
        },

        "tamanhos": (
            tamanhos
        ),

        "variacoes": (
            variacoes
        ),

        "referencia_corporal": (
            referencia_corporal
        ),

        "avatar": (
            avatar
        ),

        "comunicacao": {
            "titulo": (
                decisao_provador.get(
                    "titulo"
                )
            ),

            "descricao": (
                decisao_provador.get(
                    "descricao"
                )
            ),

            "transparencia": (
                decisao_provador.get(
                    "mensagem_transparencia"
                )
            ),
        },
    }