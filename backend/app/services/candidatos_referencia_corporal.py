def gerar_candidatos_altura_referencia(
    altura_central_cm,
    quantidade: int = 4,
    intervalo_cm: int = 3,
):
    """
    Gera candidatos de altura de referência
    para futura seleção visual no Avatar V1.

    IMPORTANTE:
    - não estima altura anatômica;
    - não corrige a calibração;
    - não altera ranking;
    - não altera recomendação;
    - apenas produz referências próximas
      para comparação visual.

    Exemplo:
    altura_central_cm = 175
    quantidade = 4
    intervalo_cm = 3

    resultado aproximado:
    172, 175, 178, 181
    """

    if altura_central_cm is None:
        return {
            "status": "indisponivel",
            "disponivel": False,
            "altura_central_cm": None,
            "quantidade": 0,
            "intervalo_cm": intervalo_cm,
            "candidatos": [],
            "experimental": True,
            "mensagem": (
                "Não há referência central suficiente "
                "para gerar candidatos visuais."
            ),
        }

    try:
        altura_central_cm = int(
            round(
                float(
                    altura_central_cm
                )
            )
        )

    except (
        TypeError,
        ValueError,
    ):
        return {
            "status": "indisponivel",
            "disponivel": False,
            "altura_central_cm": None,
            "quantidade": 0,
            "intervalo_cm": intervalo_cm,
            "candidatos": [],
            "experimental": True,
            "mensagem": (
                "A referência central recebida "
                "não é válida."
            ),
        }

    # ======================================================
    # NORMALIZAÇÃO DE PARÂMETROS
    # ======================================================

    if quantidade < 3:
        quantidade = 3

    if quantidade > 7:
        quantidade = 7

    if intervalo_cm < 1:
        intervalo_cm = 1

    if intervalo_cm > 5:
        intervalo_cm = 5

    # ======================================================
    # GERAÇÃO
    # ======================================================
    #
    # Mantemos a referência central sempre presente.
    #
    # Para quantidade par, distribuímos um candidato
    # adicional acima da referência.
    #
    # Exemplo com 4:
    # -3, 0, +3, +6
    #
    # Isso é simples e previsível para o MVP.
    # ======================================================

    deslocamentos = [0]

    passo = 1

    while len(deslocamentos) < quantidade:

        deslocamentos.append(
            -passo * intervalo_cm
        )

        if len(deslocamentos) < quantidade:
            deslocamentos.append(
                passo * intervalo_cm
            )

        passo += 1

    deslocamentos = sorted(
        deslocamentos
    )

    candidatos = []

    for indice, deslocamento in enumerate(
        deslocamentos,
        start=1,
    ):
        altura = (
            altura_central_cm
            + deslocamento
        )

        candidatos.append(
            {
                "id": (
                    f"ref_altura_{altura}"
                ),

                "altura_referencia_cm": (
                    altura
                ),

                "diferenca_central_cm": (
                    deslocamento
                ),

                "referencia_central": (
                    deslocamento == 0
                ),

                "posicao": (
                    indice
                ),

                "origem": (
                    "geracao_candidatos_referencia"
                ),

                "selecionado": False,

                "experimental": True,
            }
        )

    return {
        "status": (
            "candidatos_gerados"
        ),

        "disponivel": True,

        "altura_central_cm": (
            altura_central_cm
        ),

        "quantidade": (
            len(
                candidatos
            )
        ),

        "intervalo_cm": (
            intervalo_cm
        ),

        "candidatos": (
            candidatos
        ),

        "permite_nao_tenho_certeza": True,

        "altura_anatomica_exata": False,

        "experimental": True,

        "mensagem": (
            "Foram geradas referências próximas "
            "para futura comparação visual. "
            "Os valores não representam uma "
            "estimativa anatômica exata da altura."
        ),
    }