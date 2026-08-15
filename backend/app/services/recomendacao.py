# Ordem utilizada pelo motor para aumentar ou diminuir
# a recomendação de tamanho de forma controlada.
ORDEM_TAMANHOS = ["P", "M", "G", "GG"]


def _aumentar_tamanho(tamanho_atual: str) -> str:
    """
    Avança um nível na grade de tamanhos.

    Exemplo:
    P -> M
    M -> G
    G -> GG

    Se já estiver em GG, mantém GG.
    """

    indice_atual = ORDEM_TAMANHOS.index(tamanho_atual)

    if indice_atual < len(ORDEM_TAMANHOS) - 1:
        return ORDEM_TAMANHOS[indice_atual + 1]

    return tamanho_atual


def _diminuir_tamanho(tamanho_atual: str) -> str:
    """
    Retrocede um nível na grade de tamanhos.

    Exemplo:
    GG -> G
    G -> M
    M -> P

    Se já estiver em P, mantém P.
    """

    indice_atual = ORDEM_TAMANHOS.index(tamanho_atual)

    if indice_atual > 0:
        return ORDEM_TAMANHOS[indice_atual - 1]

    return tamanho_atual


def recomendar_tamanho(
    altura_cm: float,
    peso_kg: float,
    cintura_cm: float | None = None,
    preferencia_caimento: str | None = None,
):
    """
    Calcula um tamanho inicial utilizando altura e peso.

    A cintura e a preferência de caimento podem ajustar
    posteriormente o tamanho-base encontrado.

    As faixas utilizadas atualmente são regras provisórias
    do MVP e poderão futuramente ser substituídas pelas
    tabelas reais de medidas das marcas e produtos.
    """

    # Define o tamanho-base usando altura e peso.
    if altura_cm < 160 and peso_kg < 60:
        tamanho_base = "P"

    elif altura_cm < 170 and peso_kg < 70:
        tamanho_base = "M"

    elif altura_cm < 180 and peso_kg < 80:
        tamanho_base = "G"

    else:
        tamanho_base = "GG"

    # A cintura pode exigir um tamanho acima da estimativa inicial.
    if cintura_cm is not None and cintura_cm >= 100:
        tamanho_base = _aumentar_tamanho(tamanho_base)

    # A preferência de caimento pode alterar a recomendação final.
    if preferencia_caimento is not None:
        preferencia_caimento = preferencia_caimento.strip().lower()

        if preferencia_caimento == "solto":
            tamanho_base = _aumentar_tamanho(tamanho_base)

        elif preferencia_caimento == "justo":
            tamanho_base = _diminuir_tamanho(tamanho_base)

    return tamanho_base


def explicar_recomendacao(
    tamanho_recomendado: str,
    cintura_cm: float | None = None,
    preferencia_caimento: str | None = None,
):
    """
    Explica os principais fatores que influenciaram
    a recomendação de tamanho.
    """

    motivos = []

    # Registra quando a cintura influenciou a recomendação.
    if cintura_cm is not None and cintura_cm >= 100:
        motivos.append(
            "a medida da cintura influenciou a recomendação"
        )

    # Analisa possíveis ajustes causados pela preferência de caimento.
    if preferencia_caimento is not None:
        preferencia_normalizada = preferencia_caimento.strip().lower()

        if preferencia_normalizada == "solto":
            motivos.append(
                "preferência por caimento solto aumentou o tamanho"
            )

        elif preferencia_normalizada == "justo":
            motivos.append(
                "preferência por caimento justo diminuiu o tamanho"
            )

    # Mantém uma explicação padrão quando não houve ajustes adicionais.
    if not motivos:
        motivos.append(
            "recomendação baseada nas medidas informadas"
        )

    return {
        "tamanho_recomendado": tamanho_recomendado,
        "motivos": motivos,
    }


def calcular_confianca_recomendacao(
    altura_cm: float | None = None,
    peso_kg: float | None = None,
    cintura_cm: float | None = None,
):
    """
    Define um nível simples de confiança para a recomendação
    com base na quantidade de dados corporais disponíveis.
    """

    # Altura, peso e cintura permitem uma recomendação mais completa.
    if (
        altura_cm is not None
        and peso_kg is not None
        and cintura_cm is not None
    ):
        return "alta"

    # Altura e peso permitem uma recomendação básica do MVP.
    if altura_cm is not None and peso_kg is not None:
        return "media"

    return None


def verificar_compatibilidade_peca(
    tamanho_recomendado: str,
    largura_cm: float | None = None,
    comprimento_cm: float | None = None,
    modelagem: str | None = None,
):
    """
    Analisa características físicas e de modelagem da peça.

    Retorna observações sobre o possível caimento do produto.
    Essa análise complementa a recomendação de tamanho.
    """

    # Caso a modelagem não esteja cadastrada,
    # considera "regular" como comportamento padrão do MVP.
    if modelagem is None:
        modelagem = "regular"

    modelagem_normalizada = modelagem.strip().lower()

    observacoes = []

    # Analisa a modelagem declarada da peça.
    if modelagem_normalizada == "slim":
        observacoes.append("modelagem ajustada")

    elif modelagem_normalizada == "oversized":
        observacoes.append("modelagem ampla")

    # Analisa medidas físicas provisórias da peça.
    if largura_cm is not None and largura_cm < 50:
        observacoes.append("largura menor que 50 cm")

    if comprimento_cm is not None and comprimento_cm < 65:
        observacoes.append("comprimento menor que 65 cm")

    # Caso nenhuma característica especial tenha sido detectada.
    if not observacoes:
        observacoes.append("caimento compatível")

    return {
        "tamanho": tamanho_recomendado,
        "largura_cm": largura_cm,
        "comprimento_cm": comprimento_cm,
        "modelagem": modelagem,
        "observacoes": observacoes,
    }