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
    corrigir_delta_x,
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
    calcular_confianca_metrica,
    gerar_metricas_corporais_para_vestuario,
)

from app.services.largura_corporal_equivalente import (
    gerar_largura_corporal_equivalente,
)

from app.services.calibracao_vestuario import (
    gerar_calibracao_vestuario,
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
    Path(__file__)
    .resolve()
    .parent
    .parent
    / "models"
    / "pose_landmarker_lite.task"
)


# ==========================================================
# DIMENSÕES / GEOMETRIA DA IMAGEM
# ==========================================================

def obter_geometria_imagem(
    imagem,
):
    """
    Recupera as dimensões da imagem
    utilizada pelo MediaPipe e calcula
    seu aspect ratio.

    aspect_ratio:
        largura / altura
    """

    largura = getattr(
        imagem,
        "width",
        None,
    )

    altura = getattr(
        imagem,
        "height",
        None,
    )

    if (
        largura is None
        or altura is None
        or largura <= 0
        or altura <= 0
    ):
        return {
            "largura_px": None,
            "altura_px": None,
            "aspect_ratio": 1.0,
            "aspect_ratio_disponivel": False,
            "correcao_geometrica_2d": False,
        }

    aspect_ratio = (
        float(largura)
        / float(altura)
    )

    return {
        "largura_px": int(
            largura
        ),
        "altura_px": int(
            altura
        ),
        "aspect_ratio": round(
            aspect_ratio,
            6,
        ),
        "aspect_ratio_disponivel": True,
        "correcao_geometrica_2d": True,
    }


# ==========================================================
# COMPRIMENTO VISUAL DO TRONCO
# ==========================================================

def calcular_comprimento_tronco_relativo(
    pontos_corporais: dict,
    aspect_ratio=1.0,
):
    """
    Calcula o comprimento visual relativo
    do tronco.

    A diferença horizontal é corrigida
    pelo aspect ratio antes de ser combinada
    com a diferença vertical.
    """

    pontos_necessarios = (
        "ombro_esquerdo",
        "ombro_direito",
        "quadril_esquerdo",
        "quadril_direito",
    )

    for nome in pontos_necessarios:

        ponto = (
            pontos_corporais.get(
                nome
            )
        )

        if not ponto:
            return None

        if not ponto.get(
            "confiavel",
            False,
        ):
            return None

    ombro_esquerdo = (
        pontos_corporais[
            "ombro_esquerdo"
        ]
    )

    ombro_direito = (
        pontos_corporais[
            "ombro_direito"
        ]
    )

    quadril_esquerdo = (
        pontos_corporais[
            "quadril_esquerdo"
        ]
    )

    quadril_direito = (
        pontos_corporais[
            "quadril_direito"
        ]
    )

    centro_ombros_x = (
        (
            ombro_esquerdo["x"]
            + ombro_direito["x"]
        )
        / 2
    )

    centro_ombros_y = (
        (
            ombro_esquerdo["y"]
            + ombro_direito["y"]
        )
        / 2
    )

    centro_quadris_x = (
        (
            quadril_esquerdo["x"]
            + quadril_direito["x"]
        )
        / 2
    )

    centro_quadris_y = (
        (
            quadril_esquerdo["y"]
            + quadril_direito["y"]
        )
        / 2
    )

    diferenca_x = (
        centro_quadris_x
        - centro_ombros_x
    )

    diferenca_y = (
        centro_quadris_y
        - centro_ombros_y
    )

    diferenca_x_corrigida = (
        corrigir_delta_x(
            diferenca_x,
            aspect_ratio,
        )
    )

    comprimento_relativo = (
        (
            diferenca_x_corrigida ** 2
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
    Converte comprimento relativo
    do tronco em centímetros.
    """

    if (
        comprimento_tronco_relativo
        is None
    ):
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

    if (
        escala_cm_por_unidade
        is None
    ):
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
    aspect_ratio=1.0,
):
    """
    Estima visualmente a largura
    frontal do tórax.

    A linha horizontal é interpolada
    entre ombros e quadris.

    A distância horizontal é corrigida
    pelo aspect ratio da imagem.
    """

    pontos_necessarios = (
        "ombro_esquerdo",
        "ombro_direito",
        "quadril_esquerdo",
        "quadril_direito",
    )

    for nome in pontos_necessarios:

        ponto = (
            pontos_corporais.get(
                nome
            )
        )

        if not ponto:
            return None

        if not ponto.get(
            "confiavel",
            False,
        ):
            return None

    ombro_esquerdo = (
        pontos_corporais[
            "ombro_esquerdo"
        ]
    )

    ombro_direito = (
        pontos_corporais[
            "ombro_direito"
        ]
    )

    quadril_esquerdo = (
        pontos_corporais[
            "quadril_esquerdo"
        ]
    )

    quadril_direito = (
        pontos_corporais[
            "quadril_direito"
        ]
    )

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

    delta_x = abs(
        torax_esquerdo_x
        - torax_direito_x
    )

    largura_torax_relativa = abs(
        corrigir_delta_x(
            delta_x,
            aspect_ratio,
        )
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
    Converte a projeção frontal
    relativa do tórax para centímetros.
    """

    if (
        largura_torax_relativa
        is None
    ):
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

    if (
        escala_cm_por_unidade
        is None
    ):
        return None

    largura_torax_cm = (
        largura_torax_relativa
        * escala_cm_por_unidade
    )

    return round(
        largura_torax_cm,
        2,
    )


# ==========================================================
# PIPELINE PRINCIPAL
# ==========================================================

def detectar_pessoa(
    caminho_imagem,
    altura_cm=None,
    modelagem=None,
    preferencia_caimento="padrao",
):
    """
    Executa o pipeline visual corporal
    principal do VesteIA.

    Sprint 48:
    - correção geométrica 2D;
    - aspect ratio;
    - medidas corporais experimentais;
    - consistência geométrica;
    - análise de pose;
    - distorção;
    - calibração anatômica;
    - confiança métrica;
    - métricas semânticas para vestuário;
    - largura corporal equivalente experimental;
    - calibração específica para vestuário;
    - modelagem real da peça;
    - preferência de caimento.
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

    imagem = (
        mp.Image.create_from_file(
            str(
                caminho
            )
        )
    )

    geometria_imagem = (
        obter_geometria_imagem(
            imagem
        )
    )

    aspect_ratio = (
        geometria_imagem.get(
            "aspect_ratio",
            1.0,
        )
    )

    opcoes_base = (
        python.BaseOptions(
            model_asset_path=str(
                MODEL_PATH
            )
        )
    )

    opcoes = (
        vision.PoseLandmarkerOptions(
            base_options=(
                opcoes_base
            ),
            running_mode=(
                vision.RunningMode.IMAGE
            ),
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
        )
    )

    with (
        vision.PoseLandmarker
        .create_from_options(
            opcoes
        )
    ) as detector:

        resultado = (
            detector.detect(
                imagem
            )
        )

    pessoa_detectada = bool(
        resultado.pose_landmarks
    )

    categorias = (
        "camiseta",
        "calca",
        "vestido",
        "calcado",
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
                (
                    "Envie uma nova foto "
                    "com o corpo visível."
                )
            ],
        }

        controle_fluxo_provador = {
            "status": "fluxo_bloqueado",
            "acao": "bloquear",
            "pode_avancar": False,
            "com_ressalvas": False,
            "nova_foto_necessaria": True,
            "motivo": (
                "nenhuma_pessoa_detectada"
            ),
            "mensagem": (
                "O fluxo do provador foi "
                "bloqueado porque nenhuma "
                "pessoa foi detectada."
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
                "status": (
                    "bloqueado_por_qualidade_captura"
                ),
                "pode_analisar": False,
                "motivo": (
                    "nenhuma_pessoa_detectada"
                ),
            }
            for categoria in categorias
        }

        analise_ajuste = {
            categoria: {
                "status": "analise_bloqueada",
                "motivo": (
                    "nenhuma_pessoa_detectada"
                ),
            }
            for categoria in categorias
        }

        confianca_analise = {
            categoria: {
                "nivel": "indisponivel",
                "pontuacao": 0,
                "status": (
                    "analise_bloqueada"
                ),
            }
            for categoria in categorias
        }

        vestibilidade = {
            categoria: {
                "categoria": categoria,
                "status": "analise_bloqueada",
                "nivel_confianca": (
                    "indisponivel"
                ),
                "pontuacao_confianca": 0,
                "vestibilidade": None,
                "motivo": (
                    "nenhuma_pessoa_detectada"
                ),
            }
            for categoria in categorias
        }

        confianca_metrica = {
            "status": "dados_insuficientes",
            "nivel": "indisponivel",
            "pontuacao": 0,
            "motivos": [
                "nenhuma_pessoa_detectada"
            ],
            "mensagem": (
                "Não existem dados corporais "
                "suficientes para calcular "
                "a confiança métrica."
            ),
        }

        metricas_corporais_vestuario = {
            "status": (
                "metricas_indisponiveis"
            ),
            "metricas_liberadas": False,
            "medidas": {},
            "metricas_para_comparacao_direta": [],
            "metricas_apenas_visuais": [],
            "uso_para_recomendacao_tamanho": False,
            "mensagem": (
                "Não existem métricas corporais "
                "disponíveis para análise "
                "de vestuário."
            ),
        }

        largura_corporal_equivalente = {
            "status": "dados_insuficientes",
            "disponivel": False,
            "largura_corporal_equivalente_cm": None,
            "modelagem": (
                modelagem
            ),
            "confianca": {
                "nivel": "indisponivel",
                "pontuacao": 0,
            },
            "uso_para_comparacao_dimensional": False,
            "uso_para_recomendacao_tamanho": False,
            "mensagem": (
                "Não existem dados corporais "
                "suficientes para calcular "
                "uma largura corporal equivalente."
            ),
        }

        calibracao_vestuario = {
            "status": (
                "dados_insuficientes"
            ),
            "calibracao_disponivel": False,
            "modelagem": (
                modelagem
            ),
            "preferencia_caimento": (
                preferencia_caimento
            ),
            "comparacao_horizontal_disponivel": False,
            "comparacao_vertical_disponivel": False,
            "largura_corporal_vestuario_cm": None,
            "comprimento_corporal_vestuario_cm": None,
            "dimensoes_liberadas": [],
            "dimensoes_pendentes": [
                "horizontal",
                "vertical",
            ],
            "uso_para_recomendacao_tamanho": False,
            "experimental": True,
            "mensagem": (
                "Não existem dados corporais "
                "suficientes para executar "
                "a calibração de vestuário."
            ),
        }

        return {
            "pessoa_detectada": False,
            "landmarks_detectados": 0,

            "geometria_imagem": (
                geometria_imagem
            ),

            "correcao_geometrica_2d_aplicada": (
                geometria_imagem.get(
                    "correcao_geometrica_2d",
                    False,
                )
            ),

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

            "referencia_altura_corporal": {
                "status": (
                    "dados_corporais_indisponiveis"
                ),
                "altura_corpo_relativa": None,
            },

            "calibracao_corporal": {
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
            },

            "geometria_corporal": {
                "largura_ombros": None,
                "largura_quadril": None,
                "largura_torax_relativa": None,
                "comprimento_tronco_relativo": None,
                "aspect_ratio_aplicado": (
                    aspect_ratio
                ),
            },

            "largura_torax_relativa": None,
            "comprimento_tronco_relativo": None,

            "proporcoes_corporais": {
                "proporcao_ombros_quadril": None,
                "status": "indisponivel",
            },

            "escala_corporal": {
                "status": "escala_indisponivel",
                "escala_cm_por_unidade": None,
                "conversao_disponivel": False,
            },

            "medidas_corporais_estimadas": {
                "status": "medidas_indisponiveis",
                "largura_ombros_cm": None,
                "largura_quadril_cm": None,
                "largura_torax_cm": None,
                "comprimento_tronco_cm": None,
                "correcao_geometrica_2d_aplicada": (
                    geometria_imagem.get(
                        "correcao_geometrica_2d",
                        False,
                    )
                ),
                "uso_para_recomendacao_tamanho": False,
            },

            "consistencia_geometrica": {
                "status": "dados_insuficientes",
                "consistente": False,
                "motivos": [
                    "nenhuma pessoa detectada"
                ],
            },

            "pose_para_correcao_anatomica": {
                "status": "dados_insuficientes",
                "pose_apta": False,
                "motivos": [
                    "nenhuma pessoa detectada"
                ],
            },

            "indice_distorcao_perspectiva": {
                "status": "dados_insuficientes",
                "indice_distorcao": None,
                "nivel_distorcao": (
                    "indisponivel"
                ),
                "correcao_metrica_segura": False,
                "medidas_corrigidas": False,
            },

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

            "calibracao_anatomica": {
                "status": (
                    "bloqueada_por_qualidade_captura"
                ),
                "pronta_para_calibracao_anatomica": False,
                "medidas_corrigidas": False,
            },

            "fator_calibracao_metrica": {
                "status": (
                    "bloqueado_por_qualidade_captura"
                ),
                "fator_cm_por_unidade": None,
                "calibracao_liberada": False,
            },

            "medidas_corporais_calibradas": {
                "status": (
                    "bloqueadas_por_qualidade_captura"
                ),
                "medidas_liberadas": False,
                "largura_ombros_cm": None,
                "largura_quadril_cm": None,
                "largura_torax_cm": None,
                "comprimento_tronco_cm": None,
                "correcao_geometrica_2d_aplicada": (
                    geometria_imagem.get(
                        "correcao_geometrica_2d",
                        False,
                    )
                ),
                "medidas_corrigidas_anatomicamente": False,
                "uso_para_recomendacao_tamanho": False,
            },

            "confianca_metrica": (
                confianca_metrica
            ),

            "metricas_corporais_vestuario": (
                metricas_corporais_vestuario
            ),

            "largura_corporal_equivalente": (
                largura_corporal_equivalente
            ),

            "calibracao_vestuario": (
                calibracao_vestuario
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
                "Nenhuma pessoa detectável "
                "foi encontrada e o fluxo "
                "do provador foi bloqueado."
            ),
        }

    # ======================================================
    # LANDMARKS
    # ======================================================

    landmarks = (
        resultado.pose_landmarks[
            0
        ]
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
    # GEOMETRIA CORPORAL CORRIGIDA
    # ======================================================

    largura_ombros = (
        calcular_largura_ombros(
            pontos_corporais,
            aspect_ratio=(
                aspect_ratio
            ),
        )
    )

    largura_quadril = (
        calcular_largura_quadril(
            pontos_corporais,
            aspect_ratio=(
                aspect_ratio
            ),
        )
    )

    largura_torax_relativa = (
        calcular_largura_torax_relativa(
            pontos_corporais,
            aspect_ratio=(
                aspect_ratio
            ),
        )
    )

    comprimento_tronco_relativo = (
        calcular_comprimento_tronco_relativo(
            pontos_corporais,
            aspect_ratio=(
                aspect_ratio
            ),
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
        "aspect_ratio_aplicado": (
            aspect_ratio
        ),
        "correcao_geometrica_2d_aplicada": (
            geometria_imagem.get(
                "correcao_geometrica_2d",
                False,
            )
        ),
        "sistema_referencia": (
            "coordenadas_relativas_ao_eixo_y"
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
    # COMPRIMENTO DO TRONCO EM CM
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

    # ======================================================
    # LARGURA FRONTAL DO TÓRAX EM CM
    # ======================================================

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
    # MEDIDAS CORPORAIS EXPERIMENTAIS
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
        and escala_cm_por_unidade
        is not None
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

            "correcao_geometrica_2d_aplicada": (
                geometria_imagem.get(
                    "correcao_geometrica_2d",
                    False,
                )
            ),

            "aspect_ratio_aplicado": (
                aspect_ratio
            ),

            "medidas_corrigidas_anatomicamente": False,
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
            "correcao_geometrica_2d_aplicada": (
                geometria_imagem.get(
                    "correcao_geometrica_2d",
                    False,
                )
            ),
            "aspect_ratio_aplicado": (
                aspect_ratio
            ),
            "medidas_corrigidas_anatomicamente": False,
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
    # RESULTADO DA CAPTURA
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
            "status": (
                "bloqueada_por_qualidade_captura"
            ),
            "pronta_para_calibracao_anatomica": False,
            "medidas_corrigidas": False,
            "motivo": (
                "fluxo_provador_bloqueado"
            ),
        }

        fator_calibracao_metrica = {
            "status": (
                "bloqueado_por_qualidade_captura"
            ),
            "fator_cm_por_unidade": None,
            "calibracao_liberada": False,
        }

        medidas_corporais_calibradas = {
            "status": (
                "bloqueadas_por_qualidade_captura"
            ),
            "medidas_liberadas": False,
            "largura_ombros_cm": None,
            "largura_quadril_cm": None,
            "largura_torax_cm": None,
            "comprimento_tronco_cm": None,
            "correcao_geometrica_2d_aplicada": (
                geometria_imagem.get(
                    "correcao_geometrica_2d",
                    False,
                )
            ),
            "aspect_ratio_aplicado": (
                aspect_ratio
            ),
            "medidas_corrigidas_anatomicamente": False,
            "uso_para_recomendacao_tamanho": False,
            "motivos": [
                (
                    "captura_insuficiente_"
                    "para_continuar"
                )
            ],
        }

        confianca_metrica = {
            "status": (
                "bloqueada_por_qualidade_captura"
            ),
            "nivel": "indisponivel",
            "pontuacao": 0,
            "motivos": [
                "fluxo_provador_bloqueado"
            ],
            "mensagem": (
                "A confiança métrica não foi "
                "calculada porque a captura "
                "não possui qualidade suficiente."
            ),
        }

        metricas_corporais_vestuario = {
            "status": (
                "bloqueadas_por_qualidade_captura"
            ),
            "metricas_liberadas": False,
            "medidas": {},
            "metricas_para_comparacao_direta": [],
            "metricas_apenas_visuais": [],
            "uso_para_recomendacao_tamanho": False,
            "mensagem": (
                "As métricas corporais para "
                "vestuário foram bloqueadas "
                "pela qualidade da captura."
            ),
        }

        largura_corporal_equivalente = {
            "status": (
                "bloqueada_por_qualidade_captura"
            ),
            "disponivel": False,
            "largura_corporal_equivalente_cm": None,
            "modelagem": (
                modelagem
            ),
            "confianca": {
                "nivel": "indisponivel",
                "pontuacao": 0,
            },
            "uso_para_comparacao_dimensional": False,
            "uso_para_recomendacao_tamanho": False,
            "mensagem": (
                "A largura corporal equivalente "
                "não foi calculada porque a captura "
                "não possui qualidade suficiente."
            ),
        }

        calibracao_vestuario = {
            "status": (
                "bloqueada_por_qualidade_captura"
            ),
            "calibracao_disponivel": False,
            "modelagem": (
                modelagem
            ),
            "preferencia_caimento": (
                preferencia_caimento
            ),
            "comparacao_horizontal_disponivel": False,
            "comparacao_vertical_disponivel": False,
            "largura_corporal_vestuario_cm": None,
            "comprimento_corporal_vestuario_cm": None,
            "dimensoes_liberadas": [],
            "dimensoes_pendentes": [
                "horizontal",
                "vertical",
            ],
            "uso_para_recomendacao_tamanho": False,
            "experimental": True,
            "mensagem": (
                "A calibração de vestuário "
                "foi bloqueada porque a captura "
                "não possui qualidade suficiente."
            ),
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
                "status": (
                    "bloqueado_por_qualidade_captura"
                ),
                "pode_analisar": False,
                "motivo": (
                    "nova_foto_necessaria"
                ),
            }
            for categoria in categorias
        }

        analise_ajuste = {
            categoria: {
                "status": "analise_bloqueada",
                "motivo": (
                    "qualidade_captura_insuficiente"
                ),
            }
            for categoria in categorias
        }

        confianca_analise = {
            categoria: {
                "nivel": "indisponivel",
                "pontuacao": 0,
                "status": "analise_bloqueada",
            }
            for categoria in categorias
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
            for categoria in categorias
        }

    # ======================================================
    # FLUXO LIBERADO
    # ======================================================

    else:

        # ==================================================
        # CALIBRAÇÃO ANATÔMICA
        # ==================================================

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

        # ==================================================
        # FATOR MÉTRICO
        # ==================================================

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

        # ==================================================
        # MEDIDAS CONSOLIDADAS
        # ==================================================

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

            "correcao_geometrica_2d_aplicada": (
                geometria_imagem.get(
                    "correcao_geometrica_2d",
                    False,
                )
            ),

            "aspect_ratio_aplicado": (
                aspect_ratio
            ),

            "medidas_corrigidas_anatomicamente": False,
        }

        # ==================================================
        # CONFIANÇA MÉTRICA
        # ==================================================

        confianca_metrica = (
            calcular_confianca_metrica(
                medidas_corporais_estimadas=(
                    medidas_corporais_estimadas
                ),
                calibracao_anatomica=(
                    calibracao_anatomica
                ),
                consistencia_geometrica=(
                    consistencia_geometrica
                ),
                pose_para_correcao_anatomica=(
                    pose_para_correcao_anatomica
                ),
                indice_distorcao_perspectiva=(
                    indice_distorcao_perspectiva
                ),
            )
        )

        # ==================================================
        # MÉTRICAS SEMÂNTICAS PARA VESTUÁRIO
        # ==================================================

        metricas_corporais_vestuario = (
            gerar_metricas_corporais_para_vestuario(
                medidas_corporais_estimadas=(
                    medidas_corporais_estimadas
                ),
                indice_distorcao_perspectiva=(
                    indice_distorcao_perspectiva
                ),
                calibracao_anatomica=(
                    calibracao_anatomica
                ),
                consistencia_geometrica=(
                    consistencia_geometrica
                ),
                pose_para_correcao_anatomica=(
                    pose_para_correcao_anatomica
                ),
            )
        )

        # ==================================================
        # INTERPRETAÇÃO CORPORAL
        # ==================================================

        interpretacao_corporal = (
            interpretar_proporcoes_corporais(
                proporcoes_corporais
            )
        )

        # ==================================================
        # CORREÇÃO 2 — LARGURA CORPORAL EQUIVALENTE
        # ==================================================
        #
        # Agora a modelagem recebida pelo provador.py
        # é realmente repassada para este serviço.
        #
        # Exemplo:
        # Oversized -> oversized
        # ==================================================

        largura_corporal_equivalente = (
            gerar_largura_corporal_equivalente(
                metricas_corporais_vestuario=(
                    metricas_corporais_vestuario
                ),
                confianca_metrica=(
                    confianca_metrica
                ),
                interpretacao_corporal=(
                    interpretacao_corporal
                ),
                modelagem=(
                    modelagem
                ),
            )
        )

        # ==================================================
        # CORREÇÃO 2 — CALIBRAÇÃO PARA VESTUÁRIO
        # ==================================================
        #
        # Agora são repassados:
        #
        # - modelagem real da peça;
        # - preferência real do usuário.
        #
        # Antes ambos eram enviados como None.
        # ==================================================

        calibracao_vestuario = (
            gerar_calibracao_vestuario(
                metricas_corporais_vestuario=(
                    metricas_corporais_vestuario
                ),
                confianca_metrica=(
                    confianca_metrica
                ),
                largura_corporal_equivalente=(
                    largura_corporal_equivalente
                ),
                interpretacao_corporal=(
                    interpretacao_corporal
                ),
                modelagem=(
                    modelagem
                ),
                preferencia_caimento=(
                    preferencia_caimento
                ),
            )
        )

        # ==================================================
        # REGISTRO DA CONVERSÃO
        # ==================================================

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

        # ==================================================
        # CONTEXTO DE AJUSTE
        # ==================================================

        contexto_ajuste = (
            gerar_contexto_ajuste(
                interpretacao_corporal,
                aptidao_produtos,
            )
        )

        # ==================================================
        # ANÁLISE DE AJUSTE
        # ==================================================

        analise_ajuste = (
            gerar_analise_ajuste(
                contexto_ajuste,
                qualidade_regioes,
            )
        )

        # ==================================================
        # CONFIANÇA VISUAL
        # ==================================================

        confianca_analise = (
            calcular_confianca_analise(
                analise_ajuste
            )
        )

        # ==================================================
        # VESTIBILIDADE
        # ==================================================

        vestibilidade = {
            categoria: (
                avaliar_vestibilidade(
                    categoria,
                    contexto_ajuste,
                    confianca_analise,
                )
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

        "geometria_imagem": (
            geometria_imagem
        ),

        "correcao_geometrica_2d_aplicada": (
            geometria_imagem.get(
                "correcao_geometrica_2d",
                False,
            )
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

        # ==================================================
        # SPRINT 48 — PRECISÃO MÉTRICA
        # ==================================================

        "confianca_metrica": (
            confianca_metrica
        ),

        "metricas_corporais_vestuario": (
            metricas_corporais_vestuario
        ),

        # ==================================================
        # SPRINT 48 — REFERÊNCIA HORIZONTAL
        # ==================================================

        "largura_corporal_equivalente": (
            largura_corporal_equivalente
        ),

        # ==================================================
        # SPRINT 48 — CALIBRAÇÃO DE VESTUÁRIO
        # ==================================================

        "calibracao_vestuario": (
            calibracao_vestuario
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

        "contexto_produto_aplicado": {
            "modelagem": (
                modelagem
            ),
            "preferencia_caimento": (
                preferencia_caimento
            ),
        },

        "mensagem": (
            "Presença humana detectada, "
            "geometria 2D corrigida pelo aspect ratio, "
            "qualidade da captura avaliada, "
            "confiança métrica calculada, "
            "métricas corporais classificadas "
            "semanticamente para vestuário, "
            "largura corporal equivalente experimental "
            "calculada com a modelagem da peça, "
            "calibração de vestuário consolidada "
            "com preferência de caimento e pipeline "
            "do VesteIA executado com sucesso."
        ),
    }