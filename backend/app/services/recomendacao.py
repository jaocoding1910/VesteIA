def recomendar_tamanho(
    altura_cm: float,
    peso_kg: float,
    cintura_cm: float | None = None
):

    if altura_cm < 160 and peso_kg < 60:
        tamanho_base = "P"
    elif altura_cm < 170 and peso_kg < 70:
        tamanho_base = "M"
    elif altura_cm < 180 and peso_kg < 80:
        tamanho_base = "G"
    else:
        tamanho_base = "GG"

    # cintura pode ajustar a recomendação
    ordem_tamanhos = ["P", "M", "G", "GG"]

    if cintura_cm is not None and cintura_cm >= 100:
        indice_atual = ordem_tamanhos.index(tamanho_base)

        if indice_atual < len(ordem_tamanhos) - 1:
            tamanho_base = ordem_tamanhos[indice_atual + 1]

    return tamanho_base


def verificar_compatibilidade_peca(
        tamanho_recomendado: str,
        largura_cm: float | None = None,
        comprimento_cm: float | None = None,
        modelagem: str | None = None
):
    if modelagem is None:
        modelagem = "regular"

    compatibilidade = "compatível"

    if modelagem.lower() == "slim":
        compatibilidade = "ajustado"

    if largura_cm is not None and largura_cm < 50:
        compatibilidade = "mais ajustado"

    if comprimento_cm is not None and comprimento_cm < 65:
        compatibilidade = "curto"

    return {
        "tamanho": tamanho_recomendado,
        "largura_cm": largura_cm,
        "comprimento_cm": comprimento_cm,
        "modelagem": modelagem,
        "compatibilidade": compatibilidade
    }
