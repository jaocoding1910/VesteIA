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