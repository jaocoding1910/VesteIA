def gerar_resumo_provador(
    resultado_captura,
    controle_fluxo_provador,
):
    """
    Gera o contrato simplificado entre
    o backend do VesteIA e o frontend.

    Este objeto deve conter somente as
    informações necessárias para a interface
    decidir qual experiência apresentar.
    """

    if not resultado_captura:
        return {
            "estado": "erro_avaliacao",
            "pode_continuar": False,
            "nova_foto_necessaria": True,
            "titulo": "Não foi possível avaliar a foto",
            "mensagem": (
                "Envie uma nova imagem para continuar."
            ),
            "orientacoes": [],
        }

    status = resultado_captura.get(
        "status",
        "recusada",
    )

    mapa_estado = {
        "aprovada": "avancar",
        "aprovada_com_ressalvas": (
            "avancar_com_ressalvas"
        ),
        "recusada": "pedir_nova_foto",
    }

    estado = mapa_estado.get(
        status,
        "pedir_nova_foto",
    )

    pode_continuar = (
        resultado_captura.get(
            "pode_continuar",
            False,
        )
    )

    nova_foto_necessaria = (
        resultado_captura.get(
            "nova_foto_necessaria",
            True,
        )
    )

    return {
        "estado": estado,

        "pode_continuar": (
            pode_continuar
        ),

        "nova_foto_necessaria": (
            nova_foto_necessaria
        ),

        "titulo": (
            resultado_captura.get(
                "titulo"
            )
        ),

        "mensagem": (
            resultado_captura.get(
                "mensagem"
            )
        ),

        "orientacoes": (
            resultado_captura.get(
                "orientacoes",
                [],
            )
        ),

        "qualidade": {
            "nivel": (
                resultado_captura.get(
                    "nivel"
                )
            ),

            "pontuacao": (
                resultado_captura.get(
                    "pontuacao"
                )
            ),
        },

        "fluxo_backend": (
            controle_fluxo_provador.get(
                "status"
            )
            if controle_fluxo_provador
            else None
        ),
    }