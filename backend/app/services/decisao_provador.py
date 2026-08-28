def gerar_decisao_provador(
    resumo_provador: dict,
    compatibilidade_corpo_produto: dict,
    compatibilidade_dimensional: dict,
    resultado_dimensional: dict,
    recomendacao_tamanho_provador: dict = None,
):
    """
    Consolida os principais resultados do VesteIA
    em um contrato final amigável para o frontend.

    Inclui:
    - qualidade da captura;
    - comportamento visual da peça;
    - comparação dimensional;
    - sugestão experimental de tamanho;
    - tamanho alternativo;
    - empate técnico;
    - alternativa forte;
    - zona de decisão;
    - confiança do ranking.

    Esta camada NÃO recalcula o ranking.
    Ela apenas consolida semanticamente
    o resultado produzido pelo motor.
    """

    resumo_provador = resumo_provador or {}
    compatibilidade_corpo_produto = (
        compatibilidade_corpo_produto
        or {}
    )
    compatibilidade_dimensional = (
        compatibilidade_dimensional
        or {}
    )
    resultado_dimensional = (
        resultado_dimensional
        or {}
    )
    recomendacao_tamanho_provador = (
        recomendacao_tamanho_provador
        or {}
    )

    # ======================================================
    # CONTROLE DE FLUXO
    # ======================================================

    pode_continuar = resumo_provador.get(
        "pode_continuar",
        False,
    )

    nova_foto_necessaria = resumo_provador.get(
        "nova_foto_necessaria",
        False,
    )

    qualidade = (
        resumo_provador.get(
            "qualidade"
        )
        or {}
    )

    qualidade_foto = qualidade.get(
        "nivel"
    )

    # ======================================================
    # FOTO BLOQUEADA
    # ======================================================

    if (
        not pode_continuar
        or nova_foto_necessaria
    ):
        return {
            "status": (
                "nova_foto_necessaria"
            ),
            "pode_continuar": False,
            "titulo": (
                resumo_provador.get(
                    "titulo"
                )
                or "Precisamos de outra foto"
            ),
            "descricao": (
                resumo_provador.get(
                    "mensagem"
                )
                or (
                    "A captura atual não possui "
                    "qualidade suficiente para "
                    "continuar a análise."
                )
            ),
            "qualidade_foto": (
                qualidade_foto
            ),
            "resultado_caimento": None,
            "destaques": (
                resumo_provador.get(
                    "orientacoes",
                    [],
                )
            ),
            "confianca_visual": None,
            "comparacao_dimensional_completa": False,
            "nivel_decisao_dimensional": (
                "indisponivel"
            ),
            "recomendacao_tamanho": {
                "disponivel": False,
                "liberada": False,
                "tamanho": None,
                "tamanho_alternativo": None,
                "empate_tecnico": False,
                "alternativa_forte": False,
                "decisao_unica": False,
                "status": (
                    "bloqueada_por_qualidade_captura"
                ),
                "nivel": (
                    "indisponivel"
                ),
                "pontuacao": None,
                "preferencia_caimento": None,
                "modelagem": None,
                "ranking_parcial": False,
                "dimensoes_utilizadas": [],
                "ranking": [],
                "alternativa": None,
                "recomendacao_definitiva": False,
                "sugestao_experimental": False,
                "confianca_ranking": None,
                "zona_decisao": None,
                "explicacao_decisao": None,
                "mensagem": (
                    "A análise de tamanho foi "
                    "bloqueada pela qualidade "
                    "da captura."
                ),
            },
            "mensagem_transparencia": (
                "Envie uma nova foto antes "
                "de continuar a análise."
            ),
        }

    # ======================================================
    # RESULTADO VISUAL
    # ======================================================

    resultado_caimento = (
        resultado_dimensional.get(
            "resultado_geral"
        )
    )

    descricao = (
        resultado_dimensional.get(
            "mensagem_usuario"
        )
        or compatibilidade_corpo_produto.get(
            "mensagem"
        )
        or (
            "A análise visual da peça "
            "foi concluída."
        )
    )

    confianca = (
        compatibilidade_corpo_produto.get(
            "confianca"
        )
        or {}
    )

    confianca_visual = confianca.get(
        "nivel"
    )

    comparacao_dimensional_completa = (
        compatibilidade_dimensional.get(
            "comparacao_dimensional_completa",
            False,
        )
    )

    nivel_decisao_dimensional = (
        compatibilidade_dimensional.get(
            "nivel_decisao",
            "indisponivel",
        )
    )

    # ======================================================
    # DESTAQUES DO CAIMENTO
    # ======================================================

    destaques = []

    largura = (
        resultado_dimensional.get(
            "largura"
        )
        or {}
    )

    comprimento = (
        resultado_dimensional.get(
            "comprimento"
        )
        or {}
    )

    interpretacao_largura = largura.get(
        "interpretacao"
    )

    interpretacao_comprimento = comprimento.get(
        "interpretacao"
    )

    if interpretacao_largura == "muito_ajustado_visual":
        destaques.append(
            "Tende a ficar bem ajustada no tronco."
        )

    elif interpretacao_largura == "ajustado_visual":
        destaques.append(
            "Tende a ficar mais ajustada no tronco."
        )

    elif interpretacao_largura == "equilibrado_visual":
        destaques.append(
            "Tende a apresentar largura equilibrada no tronco."
        )

    elif interpretacao_largura == "amplo_visual":
        destaques.append(
            "Tende a ficar mais ampla no tronco."
        )

    elif interpretacao_largura == "muito_amplo_visual":
        destaques.append(
            "Tende a ficar bem ampla no tronco."
        )

    if interpretacao_comprimento == "curto_visual":
        destaques.append(
            "O comprimento tende a ficar mais curto."
        )

    elif interpretacao_comprimento == "regular_visual":
        destaques.append(
            "O comprimento tende a ficar equilibrado."
        )

    elif interpretacao_comprimento == "alongado_visual":
        destaques.append(
            "O comprimento tende a ficar mais alongado."
        )

    elif interpretacao_comprimento == "muito_alongado_visual":
        destaques.append(
            "O comprimento tende a ficar bem mais alongado."
        )

    # ======================================================
    # CONTRATO DA SUGESTÃO DE TAMANHO
    # ======================================================

    status_recomendacao = (
        recomendacao_tamanho_provador.get(
            "status"
        )
    )

    status_validos_sugestao = {
        "sugestao_tamanho_experimental_calculada",
        "sugestao_experimental_com_empate_tecnico",
        "sugestao_experimental_com_alternativa_forte",
    }

    recomendacao_disponivel = (
        bool(
            recomendacao_tamanho_provador.get(
                "disponivel",
                False,
            )
        )
        and status_recomendacao
        in status_validos_sugestao
    )

    tamanho_sugerido = (
        recomendacao_tamanho_provador.get(
            "tamanho_sugerido"
        )
        or recomendacao_tamanho_provador.get(
            "tamanho"
        )
    )

    tamanho_alternativo = (
        recomendacao_tamanho_provador.get(
            "tamanho_alternativo"
        )
    )

    pontuacao_melhor_tamanho = (
        recomendacao_tamanho_provador.get(
            "pontuacao_melhor_tamanho"
        )
    )

    ranking = (
        recomendacao_tamanho_provador.get(
            "ranking",
            [],
        )
        or []
    )

    ranking_parcial = (
        recomendacao_tamanho_provador.get(
            "ranking_parcial",
            False,
        )
    )

    dimensoes_utilizadas = (
        recomendacao_tamanho_provador.get(
            "dimensoes_utilizadas",
            [],
        )
        or []
    )

    preferencia_caimento = (
        recomendacao_tamanho_provador.get(
            "preferencia_caimento"
        )
    )

    modelagem = (
        recomendacao_tamanho_provador.get(
            "modelagem"
        )
    )

    recomendacao_definitiva = bool(
        recomendacao_tamanho_provador.get(
            "recomendacao_definitiva",
            False,
        )
    )

    sugestao_experimental = bool(
        recomendacao_tamanho_provador.get(
            "sugestao_experimental",
            False,
        )
    )

    confianca_ranking = (
        recomendacao_tamanho_provador.get(
            "confianca_ranking"
        )
        or {}
    )

    zona_decisao = (
        recomendacao_tamanho_provador.get(
            "zona_decisao"
        )
        or {}
    )

    explicacao_decisao = (
        recomendacao_tamanho_provador.get(
            "explicacao_decisao"
        )
    )

    # ======================================================
    # EMPATE / ALTERNATIVA FORTE / DECISÃO ÚNICA
    # ======================================================

    empate_tecnico = bool(
        recomendacao_tamanho_provador.get(
            "empate_tecnico",
            False,
        )
        or zona_decisao.get(
            "empate_tecnico",
            False,
        )
    )

    alternativa_forte = bool(
        recomendacao_tamanho_provador.get(
            "alternativa_forte",
            False,
        )
    )

    decisao_unica = (
        recomendacao_tamanho_provador.get(
            "decisao_unica"
        )
    )

    if decisao_unica is None:
        decisao_unica = (
            recomendacao_disponivel
            and not empate_tecnico
            and not alternativa_forte
        )

    decisao_unica = bool(
        decisao_unica
    )

    # ======================================================
    # ALTERNATIVA
    # ======================================================

    alternativa = None

    if len(ranking) > 1:
        segunda_opcao = (
            ranking[1]
            or {}
        )

        alternativa = {
            "tamanho": (
                segunda_opcao.get(
                    "tamanho"
                )
            ),
            "pontuacao": (
                segunda_opcao.get(
                    "pontuacao"
                )
            ),
            "resultado": (
                segunda_opcao.get(
                    "resultado"
                )
            ),
            "caimento_largura": (
                segunda_opcao.get(
                    "caimento_largura"
                )
            ),
            "caimento_comprimento": (
                segunda_opcao.get(
                    "caimento_comprimento"
                )
            ),
        }

        if (
            recomendacao_disponivel
            and (
                empate_tecnico
                or alternativa_forte
            )
            and not tamanho_alternativo
        ):
            tamanho_alternativo = (
                segunda_opcao.get(
                    "tamanho"
                )
            )

    # ======================================================
    # STATUS SEMÂNTICO DA RECOMENDAÇÃO
    # ======================================================

    if not recomendacao_disponivel:
        status_frontend = (
            "indisponivel"
        )

    elif empate_tecnico:
        status_frontend = (
            "sugestao_experimental_com_empate_tecnico"
        )

    elif alternativa_forte:
        status_frontend = (
            "sugestao_experimental_com_alternativa_forte"
        )

    else:
        status_frontend = (
            "sugestao_experimental"
        )

    # ======================================================
    # LIBERAÇÃO PARA O FRONTEND
    # ======================================================

    liberada_frontend = (
        recomendacao_disponivel
        and not ranking_parcial
    )

    recomendacao_tamanho = {
        "disponivel": (
            recomendacao_disponivel
        ),

        "liberada": (
            liberada_frontend
        ),

        "tamanho": (
            tamanho_sugerido
            if recomendacao_disponivel
            else None
        ),

        "tamanho_alternativo": (
            tamanho_alternativo
            if recomendacao_disponivel
            else None
        ),

        "empate_tecnico": (
            empate_tecnico
            if recomendacao_disponivel
            else False
        ),

        "alternativa_forte": (
            alternativa_forte
            if recomendacao_disponivel
            else False
        ),

        "decisao_unica": (
            decisao_unica
            if recomendacao_disponivel
            else False
        ),

        "status": (
            status_frontend
        ),

        "nivel": (
            recomendacao_tamanho_provador.get(
                "nivel",
                "indisponivel",
            )
        ),

        "pontuacao": (
            pontuacao_melhor_tamanho
        ),

        "preferencia_caimento": (
            preferencia_caimento
        ),

        "modelagem": (
            modelagem
        ),

        "ranking_parcial": (
            ranking_parcial
        ),

        "dimensoes_utilizadas": (
            dimensoes_utilizadas
        ),

        "ranking": (
            ranking
        ),

        "alternativa": (
            alternativa
        ),

        "recomendacao_definitiva": (
            recomendacao_definitiva
        ),

        "sugestao_experimental": (
            sugestao_experimental
        ),

        "confianca_ranking": (
            confianca_ranking
        ),

        "zona_decisao": (
            zona_decisao
            if zona_decisao
            else None
        ),

        "explicacao_decisao": (
            explicacao_decisao
        ),

        "mensagem": (
            recomendacao_tamanho_provador.get(
                "mensagem"
            )
        ),
    }

    # ======================================================
    # TEXTO FINAL — EMPATE TÉCNICO
    # ======================================================

    if (
        recomendacao_disponivel
        and empate_tecnico
    ):
        titulo = (
            "Dois tamanhos apresentaram "
            "resultados muito próximos"
        )

        if (
            tamanho_sugerido
            and tamanho_alternativo
        ):
            descricao = (
                f"Os tamanhos {tamanho_sugerido} "
                f"e {tamanho_alternativo} ficaram "
                "muito próximos na análise. "
                f"O tamanho {tamanho_sugerido} "
                "obteve a maior pontuação experimental, "
                "mas a alternativa também apresentou "
                "boa compatibilidade."
            )

        else:
            descricao = (
                recomendacao_tamanho_provador.get(
                    "mensagem"
                )
                or (
                    "Dois tamanhos ficaram muito "
                    "próximos na análise experimental."
                )
            )

        mensagem_transparencia = (
            recomendacao_tamanho_provador.get(
                "mensagem_transparencia"
            )
            or (
                "A análise identificou um empate técnico "
                "entre os melhores tamanhos. "
                "A sugestão continua experimental."
            )
        )

    # ======================================================
    # TEXTO FINAL — ALTERNATIVA FORTE
    # ======================================================

    elif (
        recomendacao_disponivel
        and alternativa_forte
    ):
        titulo = (
            f"{tamanho_sugerido} apresentou o melhor "
            "resultado, com uma alternativa próxima"
        )

        if tamanho_alternativo:
            descricao = (
                f"O tamanho {tamanho_sugerido} apresentou "
                "a melhor pontuação experimental, mas "
                f"{tamanho_alternativo} permanece como "
                "uma alternativa relevante. "
                "A diferença entre os dois resultados "
                "foi moderada."
            )
        else:
            descricao = (
                recomendacao_tamanho_provador.get(
                    "mensagem"
                )
                or descricao
            )

        mensagem_transparencia = (
            recomendacao_tamanho_provador.get(
                "mensagem_transparencia"
            )
            or (
                "A análise mantém uma segunda opção "
                "relevante porque a vantagem do primeiro "
                "tamanho ainda não é suficientemente "
                "ampla para uma decisão isolada."
            )
        )

    # ======================================================
    # TEXTO FINAL — DECISÃO ÚNICA EXPERIMENTAL
    # ======================================================

    elif recomendacao_disponivel:
        titulo = (
            "Veja como essa peça tende a vestir "
            "e qual tamanho apresentou "
            "o melhor equilíbrio"
        )

        descricao_recomendacao = (
            recomendacao_tamanho_provador.get(
                "mensagem"
            )
        )

        if descricao_recomendacao:
            descricao = (
                descricao_recomendacao
            )

        mensagem_transparencia = (
            recomendacao_tamanho_provador.get(
                "mensagem_transparencia"
            )
            or (
                "A sugestão de tamanho utiliza "
                "medidas visuais experimentais "
                "e ainda não representa uma "
                "recomendação antropométrica definitiva."
            )
        )

    # ======================================================
    # SEM SUGESTÃO DE TAMANHO
    # ======================================================

    else:
        titulo = (
            "Veja como essa peça tende "
            "a vestir em você"
        )

        mensagem_transparencia = (
            "A análise atual utiliza estimativas "
            "visuais e ainda não representa uma "
            "recomendação definitiva de tamanho."
        )

    # ======================================================
    # RETORNO FINAL
    # ======================================================

    return {
        "status": (
            "analise_consolidada"
        ),

        "pode_continuar": True,

        "titulo": (
            titulo
        ),

        "descricao": (
            descricao
        ),

        "qualidade_foto": (
            qualidade_foto
        ),

        "resultado_caimento": (
            resultado_caimento
        ),

        "destaques": (
            destaques
        ),

        "confianca_visual": (
            confianca_visual
        ),

        "comparacao_dimensional_completa": (
            comparacao_dimensional_completa
        ),

        "nivel_decisao_dimensional": (
            nivel_decisao_dimensional
        ),

        "recomendacao_tamanho": (
            recomendacao_tamanho
        ),

        "mensagem_transparencia": (
            mensagem_transparencia
        ),
    }