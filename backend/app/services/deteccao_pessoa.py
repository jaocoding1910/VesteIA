from pathlib import Path

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from app.services.analise_corporal import (
    extrair_landmarks_corporais,
    classificar_pontos_corporais,
    avaliar_aptidao_por_categoria,
    organizar_regioes_corporais,
    avaliar_qualidade_regioes,
)


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "pose_landmarker_lite.task"
)


def detectar_pessoa(caminho_imagem):
    """
    Detecta presença humana usando o MediaPipe,
    organiza os landmarks corporais,
    classifica a confiabilidade dos pontos,
    avalia aptidão por categoria de produto,
    organiza regiões corporais
    e avalia a qualidade de cada região.
    """

    caminho = Path(caminho_imagem)

    if not caminho.is_file():
        raise FileNotFoundError(
            "Imagem para detecção não encontrada."
        )

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            "Modelo Pose Landmarker não encontrado."
        )

    imagem = mp.Image.create_from_file(
        str(caminho)
    )

    opcoes_base = python.BaseOptions(
        model_asset_path=str(MODEL_PATH)
    )

    opcoes = vision.PoseLandmarkerOptions(
        base_options=opcoes_base,
        running_mode=vision.RunningMode.IMAGE,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
    )

    with vision.PoseLandmarker.create_from_options(
        opcoes
    ) as detector:
        resultado = detector.detect(imagem)

    pessoa_detectada = bool(
        resultado.pose_landmarks
    )

    if not pessoa_detectada:
        return {
            "pessoa_detectada": False,
            "landmarks_detectados": 0,
            "pontos_corporais": {},
            "aptidao_produtos": {
                "camiseta": False,
                "calca": False,
                "vestido": False,
                "calcado": False,
            },
            "regioes_corporais": {
                "tronco": {},
                "bracos": {},
                "pernas": {},
                "pes": {},
            },
            "qualidade_regioes": {
                "tronco": {
                    "status": "insuficiente",
                    "pontos_confiaveis": 0,
                    "total_pontos": 0,
                    "percentual_confiavel": 0,
                },
                "bracos": {
                    "status": "insuficiente",
                    "pontos_confiaveis": 0,
                    "total_pontos": 0,
                    "percentual_confiavel": 0,
                },
                "pernas": {
                    "status": "insuficiente",
                    "pontos_confiaveis": 0,
                    "total_pontos": 0,
                    "percentual_confiavel": 0,
                },
                "pes": {
                    "status": "insuficiente",
                    "pontos_confiaveis": 0,
                    "total_pontos": 0,
                    "percentual_confiavel": 0,
                },
            },
            "mensagem": (
                "Nenhuma pessoa detectável "
                "foi encontrada na imagem."
            ),
        }

    landmarks = resultado.pose_landmarks[0]

    # Converte os landmarks do MediaPipe
    # para o formato interno do VesteIA.
    landmarks_convertidos = []

    for landmark in landmarks:
        landmarks_convertidos.append(
            {
                "x": round(
                    landmark.x,
                    4,
                ),
                "y": round(
                    landmark.y,
                    4,
                ),
                "z": round(
                    landmark.z,
                    4,
                ),
                "visibilidade": round(
                    landmark.visibility,
                    4,
                ),
            }
        )

    # Traduz os índices do MediaPipe
    # para nomes corporais úteis.
    pontos_corporais = extrair_landmarks_corporais(
        landmarks_convertidos
    )

    # Classifica cada ponto como confiável
    # ou não confiável.
    pontos_corporais = classificar_pontos_corporais(
        pontos_corporais
    )

    # Avalia para quais categorias de produto
    # a foto possui informação corporal suficiente.
    aptidao_produtos = avaliar_aptidao_por_categoria(
        pontos_corporais
    )

    # Organiza os pontos em regiões corporais.
    regioes_corporais = organizar_regioes_corporais(
        pontos_corporais
    )

    # Avalia a qualidade visual de cada região.
    qualidade_regioes = avaliar_qualidade_regioes(
        regioes_corporais
    )

    return {
        "pessoa_detectada": True,
        "landmarks_detectados": len(
            landmarks
        ),
        "pontos_corporais": pontos_corporais,
        "aptidao_produtos": aptidao_produtos,
        "regioes_corporais": regioes_corporais,
        "qualidade_regioes": qualidade_regioes,
        "mensagem": (
            "Presença humana detectada, "
            "estrutura corporal organizada, "
            "aptidão por categoria avaliada "
            "e qualidade das regiões analisada."
        ),
    }