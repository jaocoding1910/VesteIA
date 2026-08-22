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
    avaliar_vestibilidade,
    avaliar_calibracao_corporal,
    calcular_altura_corpo_relativa,
)

from app.services.escala_corporal import (
    calcular_escala_corporal,
    estimar_medidas_corporais,
)

from app.services.calibracao_anatomica import (
    avaliar_calibracao_anatomica,
    avaliar_consistencia_geometrica,
)

from app.services.calibracao_metrica import (
    calcular_fator_correcao_anatomica,
)

from app.services.correcao_anatomica import (
    gerar_medidas_corporais_calibradas,
    avaliar_pose_para_correcao_anatomica,
    calcular_indice_distorcao_perspectiva,
)


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "pose_landmarker_lite.task"
)


def detectar_pessoa(
    caminho_imagem,
    altura_cm=None,
):
    """
    Detecta presença humana utilizando MediaPipe
    e executa o pipeline corporal do VesteIA.

    Pipeline atual:
    - detecção humana
    - landmarks
    - classificação dos pontos
    - aptidão por categoria
    - regiões corporais
    - qualidade visual
    - referência corporal
    - calibração corporal
    - geometria corporal
    - proporções corporais
    - escala visual
    - estimativas corporais em centímetros
    - consistência geométrica
    - avaliação da pose
    - índice de distorção da captura
    - calibração anatômica
    - fator de calibração métrica
    - consolidação das medidas corporais
    - interpretação corporal
    - contexto de ajuste
    - análise de ajuste
    - confiança
    - vestibilidade

    As medidas métricas continuam experimentais
    e ainda não estão liberadas para recomendação
    automática de tamanho.
    """

    caminho = Path(
        caminho_imagem
    )

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
        model_asset_path=str(
            MODEL_PATH
        )
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

        resultado = detector.detect(
            imagem
        )

    pessoa_detectada = bool(
        resultado.pose_landmarks
    )

    # ======================================================
    # NENHUMA PESSOA DETECTADA
    # ======================================================

    if not pessoa_detectada:

        confianca_analise = {
            categoria: {
                "nivel": "indisponivel",
                "pontuacao": 0,
                "status": "dados_insuficientes",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        contexto_ajuste = {
            categoria: {
                "status": "dados_insuficientes",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        vestibilidade = {
            categoria: avaliar_vestibilidade(
                categoria,
                contexto_ajuste,
                confianca_analise,
            )
            for categoria in contexto_ajuste
        }

        referencia_altura_corporal = {
            "status": (
                "dados_corporais_indisponiveis"
            ),
            "altura_corpo_relativa": None,
        }

        calibracao_corporal = {
            "status": (
                "dados_insuficientes_para_calibracao"
            ),
            "altura_usuario_disponivel": (
                altura_cm is not None
            ),
            "altura_cm": altura_cm,
            "corpo_inteiro_visivel": False,
            "tronco_confiavel": False,
            "pernas_confiaveis": False,
            "pes_confiaveis": False,
            "tornozelos_confiaveis": False,
            "pontas_pes_confiaveis": False,
            "conversao_cm_executada": False,
            "motivos": [
                "nenhuma pessoa detectada"
            ],
            "mensagem": (
                "Não existem dados corporais "
                "para avaliar calibração."
            ),
        }

        geometria_corporal = {
            "largura_ombros": None,
            "largura_quadril": None,
        }

        proporcoes_corporais = {
            "proporcao_ombros_quadril": None,
            "status": "indisponivel",
        }

        escala_corporal = {
            "status": "escala_indisponivel",
            "escala_cm_por_unidade": None,
            "conversao_disponivel": False,
        }

        medidas_corporais_estimadas = {
            "status": "medidas_indisponiveis",
            "largura_ombros_cm": None,
            "largura_quadril_cm": None,
        }

        consistencia_geometrica = {
            "status": "dados_insuficientes",
            "consistente": False,
            "motivos": [
                "nenhuma pessoa detectada"
            ],
        }

        pose_para_correcao_anatomica = {
            "status": "dados_insuficientes",
            "pose_apta": False,
            "motivos": [
                "nenhuma pessoa detectada"
            ],
        }

        indice_distorcao_perspectiva = {
            "status": "dados_insuficientes",
            "indice_distorcao": None,
            "nivel_distorcao": "indisponivel",
            "correcao_metrica_segura": False,
            "medidas_corrigidas": False,
        }

        calibracao_anatomica = {
            "status": "dados_insuficientes",
            "pronta_para_calibracao_anatomica": False,
            "medidas_corrigidas": False,
        }

        fator_calibracao_metrica = {
            "status": "dados_insuficientes",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

        medidas_corporais_calibradas = {
            "status": "dados_insuficientes",
            "medidas_liberadas": False,
            "largura_ombros_cm": None,
            "largura_quadril_cm": None,
            "medidas_corrigidas_anatomicamente": False,
            "uso_para_recomendacao_tamanho": False,
        }

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

            "referencia_altura_corporal": (
                referencia_altura_corporal
            ),

            "calibracao_corporal": (
                calibracao_corporal
            ),

            "geometria_corporal": (
                geometria_corporal
            ),

            "proporcoes_corporais": (
                proporcoes_corporais
            ),

            "escala_corporal": (
                escala_corporal
            ),

            "medidas_corporais_estimadas": (
                medidas_corporais_estimadas
            ),

            "consistencia_geometrica": (
                consistencia_geometrica
            ),

            "pose_para_correcao_anatomica": (
                pose_para_correcao_anatomica
            ),

            "indice_distorcao_perspectiva": (
                indice_distorcao_perspectiva
            ),

            "calibracao_anatomica": (
                calibracao_anatomica
            ),

            "fator_calibracao_metrica": (
                fator_calibracao_metrica
            ),

            "medidas_corporais_calibradas": (
                medidas_corporais_calibradas
            ),

            "interpretacao_corporal": {
                "relacao_ombros_quadril": None,
                "status": "indisponivel",
            },

            "contexto_ajuste": (
                contexto_ajuste
            ),

            "analise_ajuste": {},

            "confianca_analise": (
                confianca_analise
            ),

            "vestibilidade": (
                vestibilidade
            ),

            "mensagem": (
                "Nenhuma pessoa detectável "
                "foi encontrada na imagem."
            ),
        }

    # ======================================================
    # LANDMARKS MEDIAPIPE
    # ======================================================

    landmarks = (
        resultado.pose_landmarks[0]
    )

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

    # ======================================================
    # PONTOS CORPORAIS
    # ======================================================

    pontos_corporais = (
        extrair_landmarks_corporais(
            landmarks_convertidos
        )
    )

    pontos_corporais = (
        classificar_pontos_corporais(
            pontos_corporais
        )
    )

    # ======================================================
    # APTIDÃO POR CATEGORIA
    # ======================================================

    aptidao_produtos = (
        avaliar_aptidao_por_categoria(
            pontos_corporais
        )
    )

    # ======================================================
    # REGIÕES CORPORAIS
    # ======================================================

    regioes_corporais = (
        organizar_regioes_corporais(
            pontos_corporais
        )
    )

    qualidade_regioes = (
        avaliar_qualidade_regioes(
            regioes_corporais
        )
    )

    # ======================================================
    # REFERÊNCIA DE ALTURA CORPORAL
    # ======================================================

    referencia_altura_corporal = (
        calcular_altura_corpo_relativa(
            pontos_corporais
        )
    )

    # ======================================================
    # CALIBRAÇÃO CORPORAL
    # ======================================================

    calibracao_corporal = (
        avaliar_calibracao_corporal(
            pontos_corporais,
            qualidade_regioes,
            altura_cm=altura_cm,
        )
    )

    # ======================================================
    # GEOMETRIA CORPORAL
    # ======================================================

    largura_ombros = (
        calcular_largura_ombros(
            pontos_corporais
        )
    )

    largura_quadril = (
        calcular_largura_quadril(
            pontos_corporais
        )
    )

    geometria_corporal = {
        "largura_ombros": (
            largura_ombros
        ),

        "largura_quadril": (
            largura_quadril
        ),
    }

    # ======================================================
    # PROPORÇÕES CORPORAIS
    # ======================================================

    proporcoes_corporais = (
        calcular_proporcoes_corporais(
            geometria_corporal
        )
    )

    # ======================================================
    # ESCALA CORPORAL
    # ======================================================

    altura_corpo_relativa = (
        referencia_altura_corporal.get(
            "altura_corpo_relativa"
        )
    )

    calibracao_pronta = (
        calibracao_corporal.get(
            "status"
        )
        == "pronta_para_calibracao"
    )

    referencia_pronta = (
        referencia_altura_corporal.get(
            "status"
        )
        == "referencia_calculada"
    )

    if (
        calibracao_pronta
        and referencia_pronta
    ):

        escala_corporal = (
            calcular_escala_corporal(
                altura_usuario_cm=(
                    altura_cm
                ),
                altura_corpo_relativa=(
                    altura_corpo_relativa
                ),
            )
        )

    else:

        escala_corporal = {
            "status": "escala_indisponivel",
            "escala_cm_por_unidade": None,
            "conversao_disponivel": False,
            "motivo": (
                "calibracao_ou_referencia_"
                "corporal_indisponivel"
            ),
        }

    # ======================================================
    # ESTIMATIVAS CORPORAIS EM CM
    # ======================================================

    escala_cm_por_unidade = (
        escala_corporal.get(
            "escala_cm_por_unidade"
        )
    )

    if (
        escala_corporal.get(
            "conversao_disponivel"
        )
        and escala_cm_por_unidade is not None
    ):

        medidas_corporais_estimadas = (
            estimar_medidas_corporais(
                geometria_corporal=(
                    geometria_corporal
                ),
                escala_cm_por_unidade=(
                    escala_cm_por_unidade
                ),
            )
        )

    else:

        medidas_corporais_estimadas = {
            "status": "escala_indisponivel",

            "largura_ombros_cm": None,

            "largura_quadril_cm": None,

            "unidade": "cm",

            "tipo_medida": (
                "estimativa_visual_provisoria"
            ),

            "uso_para_recomendacao_tamanho": (
                False
            ),
        }

    # ======================================================
    # CONSISTÊNCIA GEOMÉTRICA
    # ======================================================

    consistencia_geometrica = (
        avaliar_consistencia_geometrica(
            geometria_corporal=(
                geometria_corporal
            ),

            proporcoes_corporais=(
                proporcoes_corporais
            ),

            referencia_altura_corporal=(
                referencia_altura_corporal
            ),
        )
    )

    # ======================================================
    # POSE PARA CORREÇÃO ANATÔMICA
    # ======================================================

    pose_para_correcao_anatomica = (
        avaliar_pose_para_correcao_anatomica(
            pontos_corporais=(
                pontos_corporais
            ),

            consistencia_geometrica=(
                consistencia_geometrica
            ),
        )
    )

    # ======================================================
    # ÍNDICE DE DISTORÇÃO DE PERSPECTIVA
    # ======================================================

    indice_distorcao_perspectiva = (
        calcular_indice_distorcao_perspectiva(
            pose_para_correcao_anatomica=(
                pose_para_correcao_anatomica
            )
        )
    )

    # ======================================================
    # CALIBRAÇÃO ANATÔMICA
    # ======================================================

    calibracao_anatomica = (
        avaliar_calibracao_anatomica(
            calibracao_corporal=(
                calibracao_corporal
            ),

            escala_corporal=(
                escala_corporal
            ),

            medidas_corporais_estimadas=(
                medidas_corporais_estimadas
            ),

            consistencia_geometrica=(
                consistencia_geometrica
            ),
        )
    )

    # ======================================================
    # FATOR DE CALIBRAÇÃO MÉTRICA
    # ======================================================

    fator_calibracao_metrica = (
        calcular_fator_correcao_anatomica(
            altura_usuario_cm=(
                altura_cm
            ),

            altura_corpo_relativa=(
                referencia_altura_corporal.get(
                    "altura_corpo_relativa"
                )
            ),

            consistencia_geometrica=(
                consistencia_geometrica
            ),
        )
    )

    # ======================================================
    # MEDIDAS CORPORAIS CALIBRADAS
    # ======================================================

    medidas_corporais_calibradas = (
        gerar_medidas_corporais_calibradas(
            medidas_corporais_estimadas=(
                medidas_corporais_estimadas
            ),

            calibracao_anatomica=(
                calibracao_anatomica
            ),

            fator_calibracao_metrica=(
                fator_calibracao_metrica
            ),

            consistencia_geometrica=(
                consistencia_geometrica
            ),
        )
    )

    # ======================================================
    # MARCA A CONVERSÃO PARA CM
    # ======================================================

    conversao_cm_executada = (
        medidas_corporais_estimadas.get(
            "status"
        )
        in (
            "estimativa_visual_calculada",
            "estimativa_parcial",
        )
    )

    calibracao_corporal = {
        **calibracao_corporal,

        "conversao_cm_executada": (
            conversao_cm_executada
        ),
    }

    # ======================================================
    # INTERPRETAÇÃO CORPORAL
    # ======================================================

    interpretacao_corporal = (
        interpretar_proporcoes_corporais(
            proporcoes_corporais
        )
    )

    # ======================================================
    # CONTEXTO DE AJUSTE
    # ======================================================

    contexto_ajuste = (
        gerar_contexto_ajuste(
            interpretacao_corporal,
            aptidao_produtos,
        )
    )

    # ======================================================
    # ANÁLISE DE AJUSTE
    # ======================================================

    analise_ajuste = (
        gerar_analise_ajuste(
            contexto_ajuste,
            qualidade_regioes,
        )
    )

    # ======================================================
    # CONFIANÇA DA ANÁLISE
    # ======================================================

    confianca_analise = (
        calcular_confianca_analise(
            analise_ajuste
        )
    )

    # ======================================================
    # VESTIBILIDADE
    # ======================================================

    vestibilidade = {
        categoria: avaliar_vestibilidade(
            categoria,
            contexto_ajuste,
            confianca_analise,
        )
        for categoria in contexto_ajuste
    }

    # ======================================================
    # RESULTADO FINAL
    # ======================================================

    return {
        "pessoa_detectada": True,

        "landmarks_detectados": len(
            landmarks
        ),

        "pontos_corporais": (
            pontos_corporais
        ),

        "aptidao_produtos": (
            aptidao_produtos
        ),

        "regioes_corporais": (
            regioes_corporais
        ),

        "qualidade_regioes": (
            qualidade_regioes
        ),

        "referencia_altura_corporal": (
            referencia_altura_corporal
        ),

        "calibracao_corporal": (
            calibracao_corporal
        ),

        "geometria_corporal": (
            geometria_corporal
        ),

        "proporcoes_corporais": (
            proporcoes_corporais
        ),

        "escala_corporal": (
            escala_corporal
        ),

        "medidas_corporais_estimadas": (
            medidas_corporais_estimadas
        ),

        "consistencia_geometrica": (
            consistencia_geometrica
        ),

        "pose_para_correcao_anatomica": (
            pose_para_correcao_anatomica
        ),

        "indice_distorcao_perspectiva": (
            indice_distorcao_perspectiva
        ),

        "calibracao_anatomica": (
            calibracao_anatomica
        ),

        "fator_calibracao_metrica": (
            fator_calibracao_metrica
        ),

        "medidas_corporais_calibradas": (
            medidas_corporais_calibradas
        ),

        "interpretacao_corporal": (
            interpretacao_corporal
        ),

        "contexto_ajuste": (
            contexto_ajuste
        ),

        "analise_ajuste": (
            analise_ajuste
        ),

        "confianca_analise": (
            confianca_analise
        ),

        "vestibilidade": (
            vestibilidade
        ),

        "mensagem": (
            "Presença humana detectada, "
            "estrutura corporal organizada, "
            "aptidão por categoria avaliada, "
            "qualidade das regiões analisada, "
            "referência corporal calculada, "
            "calibração corporal avaliada, "
            "geometria e proporções calculadas, "
            "escala visual processada, "
            "estimativas corporais em centímetros "
            "calculadas quando disponíveis, "
            "consistência geométrica avaliada, "
            "pose avaliada para correção anatômica, "
            "distorção de perspectiva avaliada, "
            "calibração anatômica validada, "
            "fator de calibração métrica calculado, "
            "medidas corporais consolidadas, "
            "estrutura corporal interpretada, "
            "confiança calculada e "
            "vestibilidade avaliada."
        ),
    }