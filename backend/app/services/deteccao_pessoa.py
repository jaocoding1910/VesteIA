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

from app.services.qualidade_captura import (
    avaliar_qualidade_captura,
)

from app.services.controle_fluxo_provador import (
    decidir_fluxo_provador,
)

from app.services.resultado_captura import (
    gerar_resultado_captura,
)

from app.services.resumo_provador import (
    gerar_resumo_provador,
)


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "pose_landmarker_lite.task"
)


# ==========================================================
# COMPRIMENTO VISUAL DO TRONCO
# ==========================================================

def calcular_comprimento_tronco_relativo(
    pontos_corporais: dict,
):
    """
    Calcula o comprimento visual relativo do tronco.

    Referências:
    centro dos ombros
    até
    centro dos quadris.

    O resultado permanece em coordenadas
    normalizadas da imagem.
    """

    pontos_necessarios = (
        "ombro_esquerdo",
        "ombro_direito",
        "quadril_esquerdo",
        "quadril_direito",
    )

    for nome in pontos_necessarios:
        ponto = pontos_corporais.get(nome)

        if not ponto:
            return None

        if not ponto.get(
            "confiavel",
            False,
        ):
            return None

    ombro_esquerdo = pontos_corporais[
        "ombro_esquerdo"
    ]

    ombro_direito = pontos_corporais[
        "ombro_direito"
    ]

    quadril_esquerdo = pontos_corporais[
        "quadril_esquerdo"
    ]

    quadril_direito = pontos_corporais[
        "quadril_direito"
    ]

    centro_ombros_x = (
        ombro_esquerdo["x"]
        + ombro_direito["x"]
    ) / 2

    centro_ombros_y = (
        ombro_esquerdo["y"]
        + ombro_direito["y"]
    ) / 2

    centro_quadris_x = (
        quadril_esquerdo["x"]
        + quadril_direito["x"]
    ) / 2

    centro_quadris_y = (
        quadril_esquerdo["y"]
        + quadril_direito["y"]
    ) / 2

    diferenca_x = (
        centro_quadris_x
        - centro_ombros_x
    )

    diferenca_y = (
        centro_quadris_y
        - centro_ombros_y
    )

    comprimento_relativo = (
        (
            diferenca_x ** 2
            + diferenca_y ** 2
        )
        ** 0.5
    )

    return round(
        comprimento_relativo,
        4,
    )


def converter_comprimento_tronco_cm(
    comprimento_tronco_relativo,
    escala_corporal: dict,
):
    """
    Converte o comprimento relativo do tronco
    para centímetros usando a escala corporal.

    Continua sendo uma estimativa visual
    experimental.
    """

    if comprimento_tronco_relativo is None:
        return None

    if not escala_corporal:
        return None

    if not escala_corporal.get(
        "conversao_disponivel",
        False,
    ):
        return None

    escala_cm_por_unidade = (
        escala_corporal.get(
            "escala_cm_por_unidade"
        )
    )

    if escala_cm_por_unidade is None:
        return None

    comprimento_tronco_cm = (
        comprimento_tronco_relativo
        * escala_cm_por_unidade
    )

    return round(
        comprimento_tronco_cm,
        2,
    )


# ==========================================================
# LARGURA VISUAL DO TÓRAX
# ==========================================================

def calcular_largura_torax_relativa(
    pontos_corporais: dict,
):
    """
    Estima visualmente a largura do tórax.

    O MediaPipe Pose não fornece landmarks
    específicos das laterais do tórax.

    Nesta versão experimental, a linha do tórax
    é interpolada entre ombros e quadris.

    Utilizamos aproximadamente 35% do trajeto:

    ombros
       ↓
    linha estimada do tórax
       ↓
    quadris
    """

    pontos_necessarios = (
        "ombro_esquerdo",
        "ombro_direito",
        "quadril_esquerdo",
        "quadril_direito",
    )

    for nome in pontos_necessarios:
        ponto = pontos_corporais.get(nome)

        if not ponto:
            return None

        if not ponto.get(
            "confiavel",
            False,
        ):
            return None

    ombro_esquerdo = pontos_corporais[
        "ombro_esquerdo"
    ]

    ombro_direito = pontos_corporais[
        "ombro_direito"
    ]

    quadril_esquerdo = pontos_corporais[
        "quadril_esquerdo"
    ]

    quadril_direito = pontos_corporais[
        "quadril_direito"
    ]

    fator_interpolacao = 0.35

    torax_esquerdo_x = (
        ombro_esquerdo["x"]
        + (
            quadril_esquerdo["x"]
            - ombro_esquerdo["x"]
        )
        * fator_interpolacao
    )

    torax_direito_x = (
        ombro_direito["x"]
        + (
            quadril_direito["x"]
            - ombro_direito["x"]
        )
        * fator_interpolacao
    )

    largura_torax_relativa = abs(
        torax_esquerdo_x
        - torax_direito_x
    )

    return round(
        largura_torax_relativa,
        4,
    )


def converter_largura_torax_cm(
    largura_torax_relativa,
    escala_corporal: dict,
):
    """
    Converte a largura visual relativa do tórax
    para centímetros.

    A medida é experimental e não deve ser
    tratada como medida antropométrica precisa.
    """

    if largura_torax_relativa is None:
        return None

    if not escala_corporal:
        return None

    if not escala_corporal.get(
        "conversao_disponivel",
        False,
    ):
        return None

    escala_cm_por_unidade = (
        escala_corporal.get(
            "escala_cm_por_unidade"
        )
    )

    if escala_cm_por_unidade is None:
        return None

    largura_torax_cm = (
        largura_torax_relativa
        * escala_cm_por_unidade
    )

    return round(
        largura_torax_cm,
        2,
    )


def detectar_pessoa(
    caminho_imagem,
    altura_cm=None,
):
    """
    Executa o pipeline visual corporal do VesteIA.

    Pipeline:
    - detecção humana
    - landmarks corporais
    - qualidade das regiões
    - referência relativa de altura
    - calibração corporal
    - geometria corporal
    - comprimento visual do tronco
    - largura visual estimada do tórax
    - escala visual
    - medidas experimentais em centímetros
    - consistência geométrica
    - avaliação da pose
    - distorção de perspectiva
    - qualidade geral da captura
    - controle central do fluxo
    - resultado amigável
    - resumo para frontend
    - calibração anatômica
    - fator métrico
    - medidas corporais consolidadas
    - contexto de ajuste
    - confiança
    - vestibilidade
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

        qualidade_captura = {
            "status": "dados_insuficientes",
            "pontuacao": 0,
            "nivel": "insuficiente",
            "decisao": "pedir_nova_foto",
            "nova_foto_necessaria": True,
            "orientacoes": [
                "Envie uma nova foto com o corpo visível."
            ],
        }

        controle_fluxo_provador = {
            "status": "fluxo_bloqueado",
            "acao": "bloquear",
            "pode_avancar": False,
            "com_ressalvas": False,
            "nova_foto_necessaria": True,
            "motivo": "nenhuma_pessoa_detectada",
            "mensagem": (
                "O fluxo do provador foi bloqueado "
                "porque nenhuma pessoa foi detectada."
            ),
        }

        resultado_captura = (
            gerar_resultado_captura(
                qualidade_captura=(
                    qualidade_captura
                ),
                controle_fluxo_provador=(
                    controle_fluxo_provador
                ),
            )
        )

        resumo_provador = (
            gerar_resumo_provador(
                resultado_captura=(
                    resultado_captura
                ),
                controle_fluxo_provador=(
                    controle_fluxo_provador
                ),
            )
        )

        contexto_ajuste = {
            categoria: {
                "status": "bloqueado_por_qualidade_captura",
                "pode_analisar": False,
                "motivo": "nenhuma_pessoa_detectada",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        analise_ajuste = {
            categoria: {
                "status": "analise_bloqueada",
                "motivo": "nenhuma_pessoa_detectada",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        confianca_analise = {
            categoria: {
                "nivel": "indisponivel",
                "pontuacao": 0,
                "status": "analise_bloqueada",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        vestibilidade = {
            categoria: {
                "categoria": categoria,
                "status": "analise_bloqueada",
                "nivel_confianca": "indisponivel",
                "pontuacao_confianca": 0,
                "vestibilidade": None,
                "motivo": "nenhuma_pessoa_detectada",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        referencia_altura_corporal = {
            "status": "dados_corporais_indisponiveis",
            "altura_corpo_relativa": None,
        }

        calibracao_corporal = {
            "status": "dados_insuficientes_para_calibracao",
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
            "largura_torax_relativa": None,
            "comprimento_tronco_relativo": None,
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
            "largura_torax_cm": None,
            "comprimento_tronco_cm": None,
            "uso_para_recomendacao_tamanho": False,
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
            "status": "bloqueada_por_qualidade_captura",
            "pronta_para_calibracao_anatomica": False,
            "medidas_corrigidas": False,
        }

        fator_calibracao_metrica = {
            "status": "bloqueado_por_qualidade_captura",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

        medidas_corporais_calibradas = {
            "status": "bloqueadas_por_qualidade_captura",
            "medidas_liberadas": False,
            "largura_ombros_cm": None,
            "largura_quadril_cm": None,
            "largura_torax_cm": None,
            "comprimento_tronco_cm": None,
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

            "largura_torax_relativa": None,

            "comprimento_tronco_relativo": None,

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

            "qualidade_captura": (
                qualidade_captura
            ),

            "controle_fluxo_provador": (
                controle_fluxo_provador
            ),

            "resultado_captura": (
                resultado_captura
            ),

            "resumo_provador": (
                resumo_provador
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
                "Nenhuma pessoa detectável foi encontrada "
                "e o fluxo do provador foi bloqueado."
            ),
        }

    # ======================================================
    # LANDMARKS
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
    # REFERÊNCIA DE ALTURA
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

    largura_torax_relativa = (
        calcular_largura_torax_relativa(
            pontos_corporais
        )
    )

    comprimento_tronco_relativo = (
        calcular_comprimento_tronco_relativo(
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
        "largura_torax_relativa": (
            largura_torax_relativa
        ),
        "comprimento_tronco_relativo": (
            comprimento_tronco_relativo
        ),
    }

    proporcoes_corporais = (
        calcular_proporcoes_corporais(
            geometria_corporal
        )
    )

    # ======================================================
    # ESCALA VISUAL
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
    # NOVAS MEDIDAS EM CM
    # ======================================================

    comprimento_tronco_cm = (
        converter_comprimento_tronco_cm(
            comprimento_tronco_relativo=(
                comprimento_tronco_relativo
            ),
            escala_corporal=(
                escala_corporal
            ),
        )
    )

    largura_torax_cm = (
        converter_largura_torax_cm(
            largura_torax_relativa=(
                largura_torax_relativa
            ),
            escala_corporal=(
                escala_corporal
            ),
        )
    )

    # ======================================================
    # MEDIDAS EXPERIMENTAIS EM CM
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

        medidas_corporais_estimadas = {
            **medidas_corporais_estimadas,

            "largura_torax_cm": (
                largura_torax_cm
            ),

            "comprimento_tronco_cm": (
                comprimento_tronco_cm
            ),

            "origem_largura_torax": (
                "estimativa_visual_interpolada"
            ),
        }

    else:
        medidas_corporais_estimadas = {
            "status": "escala_indisponivel",
            "largura_ombros_cm": None,
            "largura_quadril_cm": None,
            "largura_torax_cm": None,
            "comprimento_tronco_cm": None,
            "unidade": "cm",
            "tipo_medida": (
                "estimativa_visual_provisoria"
            ),
            "uso_para_recomendacao_tamanho": False,
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
    # POSE PARA CORREÇÃO
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
    # DISTORÇÃO DE PERSPECTIVA
    # ======================================================

    indice_distorcao_perspectiva = (
        calcular_indice_distorcao_perspectiva(
            pose_para_correcao_anatomica=(
                pose_para_correcao_anatomica
            )
        )
    )

    # ======================================================
    # QUALIDADE DA CAPTURA
    # ======================================================

    qualidade_captura = (
        avaliar_qualidade_captura(
            qualidade_regioes=(
                qualidade_regioes
            ),
            calibracao_corporal=(
                calibracao_corporal
            ),
            pose_para_correcao_anatomica=(
                pose_para_correcao_anatomica
            ),
            indice_distorcao_perspectiva=(
                indice_distorcao_perspectiva
            ),
        )
    )

    # ======================================================
    # CONTROLE CENTRAL DO FLUXO
    # ======================================================

    controle_fluxo_provador = (
        decidir_fluxo_provador(
            qualidade_captura=(
                qualidade_captura
            )
        )
    )

    # ======================================================
    # RESULTADO AMIGÁVEL
    # ======================================================

    resultado_captura = (
        gerar_resultado_captura(
            qualidade_captura=(
                qualidade_captura
            ),
            controle_fluxo_provador=(
                controle_fluxo_provador
            ),
        )
    )

    # ======================================================
    # RESUMO PARA FRONTEND
    # ======================================================

    resumo_provador = (
        gerar_resumo_provador(
            resultado_captura=(
                resultado_captura
            ),
            controle_fluxo_provador=(
                controle_fluxo_provador
            ),
        )
    )

    pode_avancar = (
        controle_fluxo_provador.get(
            "pode_avancar",
            False,
        )
    )

    # ======================================================
    # FLUXO BLOQUEADO
    # ======================================================

    if not pode_avancar:

        calibracao_anatomica = {
            "status": "bloqueada_por_qualidade_captura",
            "pronta_para_calibracao_anatomica": False,
            "medidas_corrigidas": False,
            "motivo": "fluxo_provador_bloqueado",
        }

        fator_calibracao_metrica = {
            "status": "bloqueado_por_qualidade_captura",
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

        medidas_corporais_calibradas = {
            "status": "bloqueadas_por_qualidade_captura",
            "medidas_liberadas": False,
            "largura_ombros_cm": None,
            "largura_quadril_cm": None,
            "largura_torax_cm": None,
            "comprimento_tronco_cm": None,
            "medidas_corrigidas_anatomicamente": False,
            "uso_para_recomendacao_tamanho": False,
            "motivos": [
                "captura_insuficiente_para_continuar"
            ],
        }

        calibracao_corporal = {
            **calibracao_corporal,
            "conversao_cm_executada": False,
        }

        interpretacao_corporal = (
            interpretar_proporcoes_corporais(
                proporcoes_corporais
            )
        )

        contexto_ajuste = {
            categoria: {
                "status": "bloqueado_por_qualidade_captura",
                "pode_analisar": False,
                "motivo": "nova_foto_necessaria",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        analise_ajuste = {
            categoria: {
                "status": "analise_bloqueada",
                "motivo": (
                    "qualidade_captura_insuficiente"
                ),
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        confianca_analise = {
            categoria: {
                "nivel": "indisponivel",
                "pontuacao": 0,
                "status": "analise_bloqueada",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

        vestibilidade = {
            categoria: {
                "categoria": categoria,
                "status": "analise_bloqueada",
                "nivel_confianca": "indisponivel",
                "pontuacao_confianca": 0,
                "vestibilidade": None,
                "motivo": "nova_foto_necessaria",
            }
            for categoria in (
                "camiseta",
                "calca",
                "vestido",
                "calcado",
            )
        }

    # ======================================================
    # FLUXO LIBERADO
    # ======================================================

    else:

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

        medidas_corporais_calibradas = {
            **medidas_corporais_calibradas,

            "largura_torax_cm": (
                largura_torax_cm
            ),

            "comprimento_tronco_cm": (
                comprimento_tronco_cm
            ),

            "origem_largura_torax": (
                "estimativa_visual_interpolada"
            ),
        }

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

        interpretacao_corporal = (
            interpretar_proporcoes_corporais(
                proporcoes_corporais
            )
        )

        contexto_ajuste = (
            gerar_contexto_ajuste(
                interpretacao_corporal,
                aptidao_produtos,
            )
        )

        analise_ajuste = (
            gerar_analise_ajuste(
                contexto_ajuste,
                qualidade_regioes,
            )
        )

        confianca_analise = (
            calcular_confianca_analise(
                analise_ajuste
            )
        )

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

        "largura_torax_relativa": (
            largura_torax_relativa
        ),

        "comprimento_tronco_relativo": (
            comprimento_tronco_relativo
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

        "qualidade_captura": (
            qualidade_captura
        ),

        "controle_fluxo_provador": (
            controle_fluxo_provador
        ),

        "resultado_captura": (
            resultado_captura
        ),

        "resumo_provador": (
            resumo_provador
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
            "qualidade da captura avaliada, "
            "fluxo do provador decidido, "
            "comprimento visual do tronco e "
            "largura visual estimada do tórax "
            "calculados quando disponíveis, "
            "resultado amigável gerado, "
            "contrato resumido preparado "
            "para o frontend e etapas posteriores "
            "executadas somente quando autorizadas."
        ),
    }