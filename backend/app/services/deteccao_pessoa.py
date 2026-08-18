from pathlib import Path

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from app.services.analise_corporal import (
    extrair_landmarks_corporais,
)


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "pose_landmarker_lite.task"
)


def detectar_pessoa(caminho_imagem):
    """
    Detecta presença humana usando o MediaPipe
    e organiza os landmarks corporais relevantes
    para o pipeline do VesteIA.
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
            "mensagem": (
                "Nenhuma pessoa detectável "
                "foi encontrada na imagem."
            ),
        }

    landmarks = resultado.pose_landmarks[0]

    # Padroniza os 33 landmarks retornados pelo MediaPipe.
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

    # A análise corporal traduz índices do MediaPipe
    # em nomes úteis para o restante do VesteIA.
    pontos_corporais = extrair_landmarks_corporais(
        landmarks_convertidos
    )

    return {
        "pessoa_detectada": True,
        "landmarks_detectados": len(
            landmarks
        ),
        "pontos_corporais": pontos_corporais,
        "mensagem": (
            "Presença humana detectada e "
            "estrutura corporal organizada."
        ),
    }