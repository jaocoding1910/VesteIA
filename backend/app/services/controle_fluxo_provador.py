def decidir_fluxo_provador(
    qualidade_captura,
):
    """
    Decide se o pipeline do provador pode continuar
    após a avaliação global da qualidade da captura.

    Decisões possíveis:
    - avancar
    - avancar_com_ressalvas
    - bloquear

    A função NÃO executa análise corporal,
    NÃO recomenda tamanho e NÃO altera medidas.
    Ela apenas controla o fluxo.
    """

    if not qualidade_captura:
        return {
            "status": "fluxo_bloqueado",
            "acao": "bloquear",
            "pode_avancar": False,
            "motivo": "qualidade_captura_indisponivel",
            "mensagem": (
                "Não foi possível avaliar a qualidade "
                "da captura."
            ),
        }

    decisao_captura = qualidade_captura.get(
        "decisao"
    )

    nova_foto_necessaria = (
        qualidade_captura.get(
            "nova_foto_necessaria",
            False,
        )
    )

    pontuacao = qualidade_captura.get(
        "pontuacao",
        0,
    )

    nivel = qualidade_captura.get(
        "nivel",
        "indisponivel",
    )

    if (
        decisao_captura == "avancar"
        and not nova_foto_necessaria
    ):
        return {
            "status": "fluxo_liberado",
            "acao": "avancar",
            "pode_avancar": True,
            "com_ressalvas": False,
            "pontuacao_captura": pontuacao,
            "nivel_captura": nivel,
            "mensagem": (
                "Captura aprovada para continuar "
                "o pipeline do provador."
            ),
        }

    if (
        decisao_captura
        == "avancar_com_ressalvas"
        and not nova_foto_necessaria
    ):
        return {
            "status": "fluxo_liberado_com_ressalvas",
            "acao": "avancar_com_ressalvas",
            "pode_avancar": True,
            "com_ressalvas": True,
            "pontuacao_captura": pontuacao,
            "nivel_captura": nivel,
            "orientacoes": qualidade_captura.get(
                "orientacoes",
                [],
            ),
            "mensagem": (
                "A captura pode continuar, "
                "mas possui limitações visuais."
            ),
        }

    return {
        "status": "fluxo_bloqueado",
        "acao": "bloquear",
        "pode_avancar": False,
        "com_ressalvas": False,
        "pontuacao_captura": pontuacao,
        "nivel_captura": nivel,
        "nova_foto_necessaria": True,
        "orientacoes": qualidade_captura.get(
            "orientacoes",
            [],
        ),
        "motivo": (
            "captura_insuficiente_para_continuar"
        ),
        "mensagem": (
            "A captura atual não possui qualidade "
            "suficiente para continuar o provador. "
            "Uma nova foto deve ser enviada."
        ),
    }