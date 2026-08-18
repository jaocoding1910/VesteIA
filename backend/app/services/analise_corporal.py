LANDMARKS_CORPORAIS = {
    # Tronco
    "ombro_esquerdo": 11,
    "ombro_direito": 12,

    # Braços
    "cotovelo_esquerdo": 13,
    "cotovelo_direito": 14,
    "punho_esquerdo": 15,
    "punho_direito": 16,

    # Quadril
    "quadril_esquerdo": 23,
    "quadril_direito": 24,

    # Pernas
    "joelho_esquerdo": 25,
    "joelho_direito": 26,
    "tornozelo_esquerdo": 27,
    "tornozelo_direito": 28,

    # Pés
    "calcanhar_esquerdo": 29,
    "calcanhar_direito": 30,
    "ponta_pe_esquerdo": 31,
    "ponta_pe_direito": 32,
}


def extrair_landmarks_corporais(landmarks: list) -> dict:
    pontos_corporais = {}

    for nome, indice in LANDMARKS_CORPORAIS.items():

        if indice >= len(landmarks):
            continue

        ponto = landmarks[indice]

        pontos_corporais[nome] = {
            "x": ponto["x"],
            "y": ponto["y"],
            "z": ponto["z"],
            "visibilidade": ponto["visibilidade"],
        }

    return pontos_corporais


def avaliar_visibilidade_ponto(
    ponto: dict,
    limite: float = 0.5
) -> bool:
    """
    Verifica se um landmark possui visibilidade
    suficiente para ser utilizado na análise corporal.
    """

    visibilidade = ponto.get("visibilidade", 0)

    return visibilidade >= limite


def classificar_pontos_corporais(
    pontos_corporais: dict,
    limite: float = 0.5
) -> dict:
    """
    Classifica os pontos corporais de acordo
    com a qualidade de visibilidade.
    """

    classificacao = {}

    for nome, ponto in pontos_corporais.items():

        confiavel = avaliar_visibilidade_ponto(
            ponto,
            limite
        )

        classificacao[nome] = {
            **ponto,
            "confiavel": confiavel
        }

    return classificacao