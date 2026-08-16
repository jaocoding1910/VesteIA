from pathlib import Path

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "pose_landmarker_lite.task"
)


def detectar_pessoa(caminho_imagem):
    """
    Detecta presença humana usando
    MediaPipe Pose Landmarker Tasks API.
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
            "mensagem": (
                "Nenhuma pessoa detectável "
                "foi encontrada na imagem."
            ),
        }

    landmarks = resultado.pose_landmarks[0]

    return {
        "pessoa_detectada": True,
        "landmarks_detectados": len(landmarks),
        "mensagem": (
            "Presença humana detectada "
            "na imagem."
        ),
    }