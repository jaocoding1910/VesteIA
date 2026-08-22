def gerar_resultado_captura(
    qualidade_captura,
    controle_fluxo_provador,
):
    """
    Gera uma resposta resumida e amigável
    para consumo pelo frontend do VesteIA.

    Esta função transforma os detalhes internos
    do pipeline em uma decisão simples para
    apresentação ao usuário.

    Estados principais:
    - aprovada
    - aprovada_com_ressalvas
    - recusada
    """

    if not qualidade_captura:
        return {
            "status": "recusada",
            "titulo": "Não foi possível avaliar a foto",
            "pode_continuar": False,
            "nova_foto_necessaria": True,
            "orientacoes": [
                "Envie uma nova foto para continuar."
            ],
        }

    if not controle_fluxo_provador:
        return {
            "status": "recusada",
            "titulo": "Não foi possível validar a captura",
            "pode_continuar": False,
            "nova_foto_necessaria": True,
            "orientacoes": qualidade_captura.get(
                "orientacoes",
                [],
            ),
        }

    pode_avancar = (
        controle_fluxo_provador.get(
            "pode_avancar",
            False,
        )
    )

    com_ressalvas = (
        controle_fluxo_provador.get(
            "com_ressalvas",
            False,
        )
    )

    pontuacao = (
        qualidade_captura.get(
            "pontuacao",
            0,
        )
    )

    nivel = (
        qualidade_captura.get(
            "nivel",
            "indisponivel",
        )
    )

    orientacoes = (
        qualidade_captura.get(
            "orientacoes",
            [],
        )
    )

    # ======================================================
    # CAPTURA APROVADA
    # ======================================================

    if (
        pode_avancar
        and not com_ressalvas
    ):
        return {
            "status": "aprovada",

            "titulo": (
                "Foto aprovada para análise"
            ),

            "pode_continuar": True,

            "nova_foto_necessaria": False,

            "pontuacao": (
                pontuacao
            ),

            "nivel": (
                nivel
            ),

            "orientacoes": (
                orientacoes
            ),

            "mensagem": (
                "A foto possui qualidade suficiente "
                "para continuar o Provador VesteIA."
            ),
        }

    # ======================================================
    # CAPTURA APROVADA COM RESSALVAS
    # ======================================================

    if (
        pode_avancar
        and com_ressalvas
    ):
        return {
            "status": "aprovada_com_ressalvas",

            "titulo": (
                "Foto adequada para análise"
            ),

            "pode_continuar": True,

            "nova_foto_necessaria": False,

            "pontuacao": (
                pontuacao
            ),

            "nivel": (
                nivel
            ),

            "orientacoes": (
                orientacoes
            ),

            "mensagem": (
                "A foto pode ser utilizada, "
                "mas uma captura melhor pode "
                "aumentar a precisão da análise."
            ),
        }

    # ======================================================
    # CAPTURA RECUSADA
    # ======================================================

    return {
        "status": "recusada",

        "titulo": (
            "Precisamos de uma nova foto"
        ),

        "pode_continuar": False,

        "nova_foto_necessaria": True,

        "pontuacao": (
            pontuacao
        ),

        "nivel": (
            nivel
        ),

        "orientacoes": (
            orientacoes
        ),

        "mensagem": (
            "A foto atual não possui qualidade "
            "suficiente para continuar a análise."
        ),
    }