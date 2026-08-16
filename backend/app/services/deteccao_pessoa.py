from pathlib import Path

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "pose_landmarker_lite.task"
)


LANDMARKS_CORPORAIS = {
    "ombro_esquerdo": 11,
    "ombro_direito": 12,
    "cotovelo_esquerdo": 13,
    "cotovelo_direito": 14,
    "punho_esquerdo": 15,
    "punho_direito": 16,
    "quadril_esquerdo": 23,
    "quadril_direito": 24,
    "joelho_esquerdo": 25,
    "joelho_direito": 26,
    "tornozelo_esquerdo": 27,
    "tornozelo_direito": 28,
}


def detectar_pessoa(caminho_imagem):
    """
    Detecta presença humana e organiza landmarks
    corporais úteis para o pipeline do VesteIA.
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

    pontos_corporais = {}

    for nome, indice in LANDMARKS_CORPORAIS.items():
        landmark = landmarks[indice]

        pontos_corporais[nome] = {
            "x": round(landmark.x, 4),
            "y": round(landmark.y, 4),
            "z": round(landmark.z, 4),
            "visibilidade": round(
                landmark.visibility,
                4,
            ),
        }

    return {
        "pessoa_detectada": True,
        "landmarks_detectados": len(landmarks),
        "pontos_corporais": pontos_corporais,
        "mensagem": (
            "Presença humana detectada e "
            "landmarks corporais estruturados."
        ),
    }