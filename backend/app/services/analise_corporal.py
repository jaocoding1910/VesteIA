import math


LANDMARKS_CORPORAIS = {
    # Cabeça / referência superior
    "nariz": 0,
    "orelha_esquerda": 7,
    "orelha_direita": 8,

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

    visibilidade = ponto.get(
        "visibilidade",
        0,
    )

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
            limite,
        )

        classificacao[nome] = {
            **ponto,
            "confiavel": confiavel,
        }

    return classificacao


def avaliar_aptidao_por_categoria(
    pontos_corporais
):
    """
    Avalia quais categorias de produto podem utilizar
    os pontos corporais detectados com confiança.
    """

    def ponto_confiavel(nome):
        ponto = pontos_corporais.get(
            nome
        )

        if not ponto:
            return False

        return ponto.get(
            "confiavel",
            False,
        )

    aptidao = {
        "camiseta": (
            ponto_confiavel("ombro_esquerdo")
            and ponto_confiavel("ombro_direito")
        ),

        "calca": (
            ponto_confiavel("quadril_esquerdo")
            and ponto_confiavel("quadril_direito")
            and ponto_confiavel("joelho_esquerdo")
            and ponto_confiavel("joelho_direito")
        ),

        "vestido": (
            ponto_confiavel("ombro_esquerdo")
            and ponto_confiavel("ombro_direito")
            and ponto_confiavel("quadril_esquerdo")
            and ponto_confiavel("quadril_direito")
        ),

        "calcado": (
            ponto_confiavel("tornozelo_esquerdo")
            and ponto_confiavel("tornozelo_direito")
            and ponto_confiavel("calcanhar_esquerdo")
            and ponto_confiavel("calcanhar_direito")
            and ponto_confiavel("ponta_pe_esquerdo")
            and ponto_confiavel("ponta_pe_direito")
        ),
    }

    return aptidao


def organizar_regioes_corporais(
    pontos_corporais
):
    """
    Organiza os pontos corporais detectados em regiões
    úteis para o pipeline do VesteIA.
    """

    regioes = {
        "tronco": [
            "ombro_esquerdo",
            "ombro_direito",
            "quadril_esquerdo",
            "quadril_direito",
        ],

        "bracos": [
            "ombro_esquerdo",
            "ombro_direito",
            "cotovelo_esquerdo",
            "cotovelo_direito",
            "punho_esquerdo",
            "punho_direito",
        ],

        "pernas": [
            "quadril_esquerdo",
            "quadril_direito",
            "joelho_esquerdo",
            "joelho_direito",
            "tornozelo_esquerdo",
            "tornozelo_direito",
        ],

        "pes": [
            "calcanhar_esquerdo",
            "calcanhar_direito",
            "ponta_pe_esquerdo",
            "ponta_pe_direito",
        ],
    }

    resultado = {}

    for nome_regiao, nomes_pontos in regioes.items():

        pontos_disponiveis = {}

        for nome_ponto in nomes_pontos:

            if nome_ponto in pontos_corporais:
                pontos_disponiveis[nome_ponto] = (
                    pontos_corporais[nome_ponto]
                )

        resultado[nome_regiao] = (
            pontos_disponiveis
        )

    return resultado


def avaliar_qualidade_regioes(
    regioes_corporais
):
    """
    Avalia a qualidade de cada região corporal
    com base na quantidade de pontos confiáveis.

    Retorna:
    - apta
    - parcial
    - insuficiente
    """

    resultado = {}

    for nome_regiao, pontos in regioes_corporais.items():

        total_pontos = len(
            pontos
        )

        pontos_confiaveis = sum(
            1
            for ponto in pontos.values()
            if ponto.get(
                "confiavel",
                False,
            )
        )

        if total_pontos == 0:
            percentual = 0

        else:
            percentual = (
                pontos_confiaveis
                / total_pontos
            )

        if percentual >= 0.75:
            status = "apta"

        elif percentual >= 0.50:
            status = "parcial"

        else:
            status = "insuficiente"

        resultado[nome_regiao] = {
            "status": status,
            "pontos_confiaveis": pontos_confiaveis,
            "total_pontos": total_pontos,
            "percentual_confiavel": round(
                percentual,
                2,
            ),
        }

    return resultado


def calcular_distancia_2d(
    ponto_a,
    ponto_b
):
    """
    Calcula a distância bidimensional entre dois
    pontos corporais usando as coordenadas x e y.
    """

    if not ponto_a or not ponto_b:
        return None

    delta_x = (
        ponto_b["x"]
        - ponto_a["x"]
    )

    delta_y = (
        ponto_b["y"]
        - ponto_a["y"]
    )

    distancia = math.sqrt(
        delta_x ** 2
        + delta_y ** 2
    )

    return round(
        distancia,
        4,
    )


def calcular_largura_ombros(
    pontos_corporais
):
    """
    Calcula a largura relativa dos ombros
    usando os landmarks esquerdo e direito.
    """

    ombro_esquerdo = pontos_corporais.get(
        "ombro_esquerdo"
    )

    ombro_direito = pontos_corporais.get(
        "ombro_direito"
    )

    if (
        not ombro_esquerdo
        or not ombro_direito
    ):
        return None

    if not ombro_esquerdo.get(
        "confiavel",
        False,
    ):
        return None

    if not ombro_direito.get(
        "confiavel",
        False,
    ):
        return None

    return calcular_distancia_2d(
        ombro_esquerdo,
        ombro_direito,
    )


def calcular_largura_quadril(
    pontos_corporais
):
    """
    Calcula a largura relativa do quadril
    usando os landmarks esquerdo e direito.
    """

    quadril_esquerdo = pontos_corporais.get(
        "quadril_esquerdo"
    )

    quadril_direito = pontos_corporais.get(
        "quadril_direito"
    )

    if (
        not quadril_esquerdo
        or not quadril_direito
    ):
        return None

    if not quadril_esquerdo.get(
        "confiavel",
        False,
    ):
        return None

    if not quadril_direito.get(
        "confiavel",
        False,
    ):
        return None

    return calcular_distancia_2d(
        quadril_esquerdo,
        quadril_direito,
    )


def calcular_proporcoes_corporais(
    geometria_corporal
):
    """
    Calcula proporções corporais relativas
    a partir da geometria detectada na imagem.

    Não representa medidas reais
    em centímetros.
    """

    largura_ombros = (
        geometria_corporal.get(
            "largura_ombros"
        )
    )

    largura_quadril = (
        geometria_corporal.get(
            "largura_quadril"
        )
    )

    if (
        not largura_ombros
        or not largura_quadril
    ):
        return {
            "proporcao_ombros_quadril": None,
            "status": "dados_insuficientes",
        }

    proporcao = (
        largura_ombros
        / largura_quadril
    )

    return {
        "proporcao_ombros_quadril": round(
            proporcao,
            4,
        ),
        "status": "calculada",
    }


def interpretar_proporcoes_corporais(
    proporcoes_corporais
):
    """
    Interpreta as proporções corporais relativas
    calculadas pelo pipeline visual do VesteIA.

    A interpretação é geométrica e não representa
    medidas corporais reais em centímetros.
    """

    proporcao = proporcoes_corporais.get(
        "proporcao_ombros_quadril"
    )

    if proporcao is None:
        return {
            "relacao_ombros_quadril": (
                "indeterminada"
            ),
            "status": "dados_insuficientes",
        }

    if proporcao > 1.10:
        relacao = "ombros_mais_largos"

    elif proporcao < 0.90:
        relacao = "quadril_mais_largo"

    else:
        relacao = (
            "proporcoes_equilibradas"
        )

    return {
        "relacao_ombros_quadril": relacao,
        "status": "interpretada",
    }


def gerar_contexto_ajuste(
    interpretacao_corporal,
    aptidao_produtos,
):
    """
    Gera contexto estrutural para futuras análises
    de ajuste das peças no VesteIA.

    Não recomenda tamanho e não representa
    medidas corporais reais.
    """

    relacao = interpretacao_corporal.get(
        "relacao_ombros_quadril"
    )

    contexto = {}

    if aptidao_produtos.get(
        "camiseta"
    ):
        contexto["camiseta"] = {
            "regiao_prioritaria": "tronco",
            "relacao_corporal": relacao,
            "status": "pronta_para_analise",
        }

    else:
        contexto["camiseta"] = {
            "status": "dados_insuficientes",
        }

    if aptidao_produtos.get(
        "calca"
    ):
        contexto["calca"] = {
            "regiao_prioritaria": (
                "pernas_quadril"
            ),
            "relacao_corporal": relacao,
            "status": "pronta_para_analise",
        }

    else:
        contexto["calca"] = {
            "status": "dados_insuficientes",
        }

    if aptidao_produtos.get(
        "vestido"
    ):
        contexto["vestido"] = {
            "regiao_prioritaria": (
                "corpo_integrado"
            ),
            "relacao_corporal": relacao,
            "status": "pronta_para_analise",
        }

    else:
        contexto["vestido"] = {
            "status": "dados_insuficientes",
        }

    if aptidao_produtos.get(
        "calcado"
    ):
        contexto["calcado"] = {
            "regiao_prioritaria": "pes",
            "status": "pronta_para_analise",
        }

    else:
        contexto["calcado"] = {
            "status": "dados_insuficientes",
        }

    return contexto


def gerar_analise_ajuste(
    contexto_ajuste,
    qualidade_regioes,
):
    """
    Gera uma análise preliminar de ajuste
    para cada categoria de produto.

    Esta função ainda não recomenda tamanho
    nem determina se uma peça ficará apertada
    ou folgada.
    """

    analise = {}

    mapa_regioes = {
        "camiseta": [
            "tronco",
            "bracos",
        ],

        "calca": [
            "pernas",
            "tronco",
        ],

        "vestido": [
            "tronco",
            "pernas",
        ],

        "calcado": [
            "pes",
        ],
    }

    for categoria, regioes in mapa_regioes.items():

        contexto_categoria = (
            contexto_ajuste.get(
                categoria,
                {},
            )
        )

        if (
            contexto_categoria.get(
                "status"
            )
            != "pronta_para_analise"
        ):
            analise[categoria] = {
                "status": (
                    "dados_insuficientes"
                ),
                "regioes_analisadas": regioes,
            }

            continue

        qualidade_categoria = {}

        for regiao in regioes:
            qualidade_categoria[regiao] = (
                qualidade_regioes.get(
                    regiao,
                    {
                        "status": (
                            "insuficiente"
                        ),
                    },
                )
            )

        analise[categoria] = {
            "status": "analise_preparada",
            "regiao_prioritaria": (
                contexto_categoria.get(
                    "regiao_prioritaria"
                )
            ),
            "relacao_corporal": (
                contexto_categoria.get(
                    "relacao_corporal"
                )
            ),
            "regioes_analisadas": regioes,
            "qualidade_regioes": (
                qualidade_categoria
            ),
        }

    return analise


def calcular_confianca_analise(
    analise_ajuste,
):
    """
    Calcula o nível de confiança da análise
    visual para cada categoria de produto.

    A confiança representa a qualidade dos
    dados corporais disponíveis na imagem.

    Não representa confiança de tamanho
    nem de medidas físicas reais.
    """

    resultado = {}

    for categoria, analise in (
        analise_ajuste.items()
    ):

        if (
            analise.get("status")
            != "analise_preparada"
        ):
            resultado[categoria] = {
                "nivel": "indisponivel",
                "pontuacao": 0,
                "status": (
                    "dados_insuficientes"
                ),
            }

            continue

        qualidade_regioes = (
            analise.get(
                "qualidade_regioes",
                {},
            )
        )

        percentuais = []

        for qualidade in (
            qualidade_regioes.values()
        ):
            percentual = qualidade.get(
                "percentual_confiavel",
                0,
            )

            percentuais.append(
                percentual
            )

        if not percentuais:
            resultado[categoria] = {
                "nivel": "indisponivel",
                "pontuacao": 0,
                "status": (
                    "dados_insuficientes"
                ),
            }

            continue

        pontuacao = round(
            sum(percentuais)
            / len(percentuais),
            2,
        )

        if pontuacao >= 0.85:
            nivel = "alta"

        elif pontuacao >= 0.60:
            nivel = "moderada"

        else:
            nivel = "baixa"

        resultado[categoria] = {
            "nivel": nivel,
            "pontuacao": pontuacao,
            "status": "calculada",
        }

    return resultado


def avaliar_vestibilidade(
    categoria,
    contexto_ajuste,
    confianca_analise,
):
    """
    Avalia a disponibilidade e a qualidade
    da análise visual de vestibilidade para
    determinada categoria de produto.

    Esta etapa ainda não determina tamanho,
    aperto ou folga da peça.

    A avaliação representa somente a qualidade
    dos dados corporais disponíveis para que
    uma análise de vestibilidade seja realizada.
    """

    contexto = contexto_ajuste.get(
        categoria,
        {},
    )

    confianca = confianca_analise.get(
        categoria,
        {},
    )

    nivel_confianca = confianca.get(
        "nivel",
        "indisponivel",
    )

    pontuacao = confianca.get(
        "pontuacao",
        0,
    )

    if (
        contexto.get("status")
        != "pronta_para_analise"
        or nivel_confianca
        == "indisponivel"
    ):
        return {
            "categoria": categoria,
            "status": "dados_insuficientes",
            "nivel_confianca": (
                nivel_confianca
            ),
            "pontuacao_confianca": (
                pontuacao
            ),
            "vestibilidade": None,
        }

    if nivel_confianca == "alta":
        vestibilidade = (
            "avaliacao_visual_confiavel"
        )

        status = (
            "apta_para_analise"
        )

    elif nivel_confianca == "moderada":
        vestibilidade = (
            "avaliacao_visual_parcial"
        )

        status = (
            "apta_com_ressalvas"
        )

    else:
        vestibilidade = (
            "dados_visuais_limitados"
        )

        status = (
            "analise_limitada"
        )

    return {
        "categoria": categoria,
        "status": status,
        "nivel_confianca": nivel_confianca,
        "pontuacao_confianca": pontuacao,
        "regiao_prioritaria": contexto.get(
            "regiao_prioritaria"
        ),
        "relacao_corporal": contexto.get(
            "relacao_corporal"
        ),
        "vestibilidade": vestibilidade,
    }


def avaliar_calibracao_corporal(
    pontos_corporais,
    qualidade_regioes,
    altura_cm=None,
):
    """
    Avalia se a imagem possui dados corporais
    suficientes para uma futura calibração física.

    Esta etapa NÃO converte coordenadas normalizadas
    para centímetros.

    Ela apenas verifica se existe informação visual
    adequada para uma futura estimativa corporal.
    """

    def ponto_confiavel(nome):
        ponto = pontos_corporais.get(
            nome,
            {},
        )

        return ponto.get(
            "confiavel",
            False,
        )

    tronco_status = qualidade_regioes.get(
        "tronco",
        {},
    ).get(
        "status",
        "insuficiente",
    )

    pernas_status = qualidade_regioes.get(
        "pernas",
        {},
    ).get(
        "status",
        "insuficiente",
    )

    pes_status = qualidade_regioes.get(
        "pes",
        {},
    ).get(
        "status",
        "insuficiente",
    )

    altura_usuario_disponivel = (
        altura_cm is not None
        and altura_cm > 0
    )

    tronco_confiavel = (
        tronco_status == "apta"
    )

    pernas_confiaveis = (
        pernas_status == "apta"
    )

    pes_confiaveis = (
        pes_status == "apta"
    )

    tornozelos_confiaveis = (
        ponto_confiavel(
            "tornozelo_esquerdo"
        )
        and ponto_confiavel(
            "tornozelo_direito"
        )
    )

    pontas_pes_confiaveis = (
        ponto_confiavel(
            "ponta_pe_esquerdo"
        )
        and ponto_confiavel(
            "ponta_pe_direito"
        )
    )

    corpo_inteiro_visivel = (
        tronco_confiavel
        and pernas_confiaveis
        and tornozelos_confiaveis
        and pontas_pes_confiaveis
    )

    motivos = []

    if not altura_usuario_disponivel:
        motivos.append(
            "altura do usuário não informada"
        )

    if not tronco_confiavel:
        motivos.append(
            "região do tronco sem qualidade suficiente"
        )

    if not pernas_confiaveis:
        motivos.append(
            "região das pernas parcialmente visível "
            "ou com baixa confiabilidade"
        )

    if not tornozelos_confiaveis:
        motivos.append(
            "tornozelos com baixa confiabilidade"
        )

    if not pontas_pes_confiaveis:
        motivos.append(
            "pés fora do enquadramento "
            "ou com baixa confiabilidade"
        )

    if (
        altura_usuario_disponivel
        and corpo_inteiro_visivel
    ):
        status = "pronta_para_calibracao"

    elif (
        altura_usuario_disponivel
        and tronco_confiavel
    ):
        status = "calibracao_parcial"

    else:
        status = (
            "dados_insuficientes_para_calibracao"
        )

    return {
        "status": status,
        "altura_usuario_disponivel": (
            altura_usuario_disponivel
        ),
        "altura_cm": (
            altura_cm
            if altura_usuario_disponivel
            else None
        ),
        "corpo_inteiro_visivel": (
            corpo_inteiro_visivel
        ),
        "tronco_confiavel": (
            tronco_confiavel
        ),
        "pernas_confiaveis": (
            pernas_confiaveis
        ),
        "pes_confiaveis": (
            pes_confiaveis
        ),
        "tornozelos_confiaveis": (
            tornozelos_confiaveis
        ),
        "pontas_pes_confiaveis": (
            pontas_pes_confiaveis
        ),
        "conversao_cm_executada": False,
        "motivos": motivos,
        "mensagem": (
            "Qualidade da imagem avaliada "
            "para futura calibração corporal."
        ),
    }


def calcular_altura_corpo_relativa(
    pontos_corporais,
):
    """
    Calcula uma referência vertical corporal
    mais completa usando pontos superiores
    da cabeça/rosto e pontos inferiores dos pés.

    Esta medida continua sendo relativa e
    NÃO representa altura real em centímetros.
    """

    nariz = pontos_corporais.get(
        "nariz"
    )

    orelha_esquerda = pontos_corporais.get(
        "orelha_esquerda"
    )

    orelha_direita = pontos_corporais.get(
        "orelha_direita"
    )

    ponta_pe_esquerdo = pontos_corporais.get(
        "ponta_pe_esquerdo"
    )

    ponta_pe_direito = pontos_corporais.get(
        "ponta_pe_direito"
    )

    pontos_superiores = [
        ponto
        for ponto in (
            nariz,
            orelha_esquerda,
            orelha_direita,
        )
        if (
            ponto
            and ponto.get(
                "confiavel",
                False,
            )
        )
    ]

    pontos_inferiores = [
        ponto
        for ponto in (
            ponta_pe_esquerdo,
            ponta_pe_direito,
        )
        if (
            ponto
            and ponto.get(
                "confiavel",
                False,
            )
        )
    ]

    if not pontos_superiores:
        return {
            "status": (
                "referencia_superior_nao_confiavel"
            ),
            "altura_corpo_relativa": None,
        }

    if not pontos_inferiores:
        return {
            "status": (
                "referencia_inferior_nao_confiavel"
            ),
            "altura_corpo_relativa": None,
        }

    y_superior = min(
        ponto["y"]
        for ponto in pontos_superiores
    )

    y_inferior = max(
        ponto["y"]
        for ponto in pontos_inferiores
    )

    altura_relativa = (
        y_inferior
        - y_superior
    )

    if altura_relativa <= 0:
        return {
            "status": (
                "referencia_corporal_invalida"
            ),
            "altura_corpo_relativa": None,
        }

    return {
        "status": "referencia_calculada",
        "altura_corpo_relativa": round(
            altura_relativa,
            4,
        ),
        "referencia_superior": (
            "face_cabeca_observavel"
        ),
        "referencia_inferior": "pontas_dos_pes",
        "unidade": (
            "coordenadas_normalizadas"
        ),
        "observacao": (
            "Referência corporal visual aproximada; "
            "não representa diretamente a altura "
            "anatômica total."
        ),
    }