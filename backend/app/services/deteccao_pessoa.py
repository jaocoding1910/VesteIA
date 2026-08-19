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
    calcular_largura_ombros,
    calcular_largura_quadril,
    calcular_proporcoes_corporais,
    interpretar_proporcoes_corporais,
    gerar_contexto_ajuste,
    gerar_analise_ajuste,
    calcular_confianca_analise,
)


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "pose_landmarker_lite.task"
)


def detectar_pessoa(caminho_imagem):
    """
    Executa o pipeline de análise corporal do VesteIA.

    Detecta a pessoa, organiza landmarks,
    avalia qualidade e aptidão por categoria,
    calcula geometria e proporções corporais,
    prepara a análise de ajuste
    e calcula a confiança da análise.
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

            "geometria_corporal": {
                "largura_ombros": None,
                "largura_quadril": None,
            },

            "proporcoes_corporais": {
                "proporcao_ombros_quadril": None,
                "status": "dados_insuficientes",
            },

            "interpretacao_corporal": {
                "relacao_ombros_quadril": "indeterminada",
                "status": "dados_insuficientes",
            },

            "contexto_ajuste": {
                "camiseta": {
                    "status": "dados_insuficientes",
                },
                "calca": {
                    "status": "dados_insuficientes",
                },
                "vestido": {
                    "status": "dados_insuficientes",
                },
                "calcado": {
                    "status": "dados_insuficientes",
                },
            },

            "analise_ajuste": {
                "camiseta": {
                    "status": "dados_insuficientes",
                    "regioes_analisadas": [
                        "tronco",
                        "bracos",
                    ],
                },
                "calca": {
                    "status": "dados_insuficientes",
                    "regioes_analisadas": [
                        "pernas",
                        "tronco",
                    ],
                },
                "vestido": {
                    "status": "dados_insuficientes",
                    "regioes_analisadas": [
                        "tronco",
                        "pernas",
                    ],
                },
                "calcado": {
                    "status": "dados_insuficientes",
                    "regioes_analisadas": [
                        "pes",
                    ],
                },
            },

            "confianca_analise": {
                "camiseta": {
                    "nivel": "indisponivel",
                    "pontuacao": 0,
                    "status": "dados_insuficientes",
                },
                "calca": {
                    "nivel": "indisponivel",
                    "pontuacao": 0,
                    "status": "dados_insuficientes",
                },
                "vestido": {
                    "nivel": "indisponivel",
                    "pontuacao": 0,
                    "status": "dados_insuficientes",
                },
                "calcado": {
                    "nivel": "indisponivel",
                    "pontuacao": 0,
                    "status": "dados_insuficientes",
                },
            },

            "mensagem": (
                "Nenhuma pessoa detectável "
                "foi encontrada na imagem."
            ),
        }

    landmarks = resultado.pose_landmarks[0]

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

    # Pontos corporais semânticos.
    pontos_corporais = extrair_landmarks_corporais(
        landmarks_convertidos
    )

    # Confiabilidade individual dos pontos.
    pontos_corporais = classificar_pontos_corporais(
        pontos_corporais
    )

    # Aptidão da imagem por categoria.
    aptidao_produtos = avaliar_aptidao_por_categoria(
        pontos_corporais
    )

    # Organização das regiões corporais.
    regioes_corporais = organizar_regioes_corporais(
        pontos_corporais
    )

    # Qualidade visual das regiões.
    qualidade_regioes = avaliar_qualidade_regioes(
        regioes_corporais
    )

    # Geometria corporal relativa.
    largura_ombros = calcular_largura_ombros(
        pontos_corporais
    )

    largura_quadril = calcular_largura_quadril(
        pontos_corporais
    )

    geometria_corporal = {
        "largura_ombros": largura_ombros,
        "largura_quadril": largura_quadril,
    }

    # Proporções corporais relativas.
    proporcoes_corporais = calcular_proporcoes_corporais(
        geometria_corporal
    )

    # Interpretação estrutural.
    interpretacao_corporal = interpretar_proporcoes_corporais(
        proporcoes_corporais
    )

    # Contexto por categoria de produto.
    contexto_ajuste = gerar_contexto_ajuste(
        interpretacao_corporal,
        aptidao_produtos,
    )

    # Análise preliminar de ajuste.
    analise_ajuste = gerar_analise_ajuste(
        contexto_ajuste,
        qualidade_regioes,
    )

    # Confiança consolidada da análise visual.
    confianca_analise = calcular_confianca_analise(
        analise_ajuste
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
        "geometria_corporal": geometria_corporal,
        "proporcoes_corporais": proporcoes_corporais,
        "interpretacao_corporal": interpretacao_corporal,
        "contexto_ajuste": contexto_ajuste,
        "analise_ajuste": analise_ajuste,
        "confianca_analise": confianca_analise,
        "mensagem": (
            "Presença humana detectada, "
            "estrutura corporal organizada, "
            "aptidão por categoria avaliada, "
            "qualidade das regiões analisada, "
            "geometria e proporções calculadas, "
            "estrutura corporal interpretada, "
            "análise de ajuste preparada "
            "e confiança da análise calculada."
        ),
    }