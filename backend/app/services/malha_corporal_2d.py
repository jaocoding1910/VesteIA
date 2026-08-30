def _numero(valor):
    """
    Converte um valor para float de forma segura.
    """

    if valor is None:
        return None

    try:
        return float(valor)

    except (
        TypeError,
        ValueError,
    ):
        return None


def _arredondar(
    valor,
    casas=4,
):
    """
    Arredonda um valor numérico
    de forma segura.
    """

    valor = _numero(
        valor
    )

    if valor is None:
        return None

    return round(
        valor,
        casas,
    )


def _ponto_valido(
    ponto,
):
    """
    Verifica se um landmark possui
    coordenadas 2D utilizáveis.
    """

    if not isinstance(
        ponto,
        dict,
    ):
        return False

    x = _numero(
        ponto.get("x")
    )

    y = _numero(
        ponto.get("y")
    )

    if (
        x is None
        or y is None
    ):
        return False

    if not ponto.get(
        "confiavel",
        False,
    ):
        return False

    return True


def _extrair_ponto(
    pontos,
    nome,
):
    """
    Extrai somente as informações necessárias
    para construção da malha visual.
    """

    ponto = pontos.get(
        nome
    )

    if not _ponto_valido(
        ponto
    ):
        return None

    return {
        "x": _arredondar(
            ponto.get("x")
        ),

        "y": _arredondar(
            ponto.get("y")
        ),

        "z": _arredondar(
            ponto.get("z")
        ),

        "visibilidade": _arredondar(
            ponto.get(
                "visibilidade"
            )
        ),

        "confiavel": True,
    }


def _centro_pontos(
    ponto_a,
    ponto_b,
):
    """
    Calcula o ponto central entre
    dois landmarks confiáveis.
    """

    if (
        ponto_a is None
        or ponto_b is None
    ):
        return None

    return {
        "x": _arredondar(
            (
                ponto_a["x"]
                + ponto_b["x"]
            )
            / 2
        ),

        "y": _arredondar(
            (
                ponto_a["y"]
                + ponto_b["y"]
            )
            / 2
        ),

        "tipo": (
            "ponto_derivado"
        ),
    }


def _normalizar_ponto(
    ponto,
    limite_superior,
    altura_visual,
):
    """
    Converte a coordenada vertical original
    da fotografia para o espaço corporal
    normalizado do avatar.

    O eixo Y passa a representar:

    topo visual do corpo = 0.0
    base visual do corpo = 1.0

    O eixo X permanece inicialmente no
    sistema normalizado da imagem.

    A centralização horizontal será tratada
    separadamente para não destruir
    a geometria observada.
    """

    if ponto is None:
        return None

    x = _numero(
        ponto.get("x")
    )

    y = _numero(
        ponto.get("y")
    )

    if (
        x is None
        or y is None
        or altura_visual is None
        or altura_visual <= 0
    ):
        return None

    y_normalizado = (
        (
            y
            - limite_superior
        )
        / altura_visual
    )

    return {
        "x_imagem": _arredondar(
            x
        ),

        "y_corpo": _arredondar(
            y_normalizado
        ),

        "origem": (
            "landmark_normalizado"
        ),
    }


def gerar_malha_corporal_2d_v1(
    deteccao: dict,
    estado_renderizacao_avatar: dict,
):
    """
    Gera a Malha Corporal 2D V1 do VesteIA.

    A malha é uma representação estrutural
    desenhável baseada nos landmarks reais
    observados na fotografia.

    Esta camada NÃO:
    - calcula centímetros;
    - estima altura física;
    - estima peso;
    - estima circunferências;
    - recomenda tamanho;
    - modifica a Sprint 48;
    - gera imagem;
    - gera textura;
    - gera anatomia 3D;
    - inventa articulações ausentes.

    A saída prepara pontos, centros e
    segmentos para o futuro renderer 2D.
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if not isinstance(
        deteccao,
        dict,
    ):
        return {
            "versao": "malha_corporal_2d_v1",
            "status": "deteccao_invalida",
            "disponivel": False,
            "pronta_para_renderer": False,
            "renderizada": False,
        }

    if not isinstance(
        estado_renderizacao_avatar,
        dict,
    ):
        return {
            "versao": "malha_corporal_2d_v1",
            "status": "estado_renderizacao_invalido",
            "disponivel": False,
            "pronta_para_renderer": False,
            "renderizada": False,
        }

    if not estado_renderizacao_avatar.get(
        "pronto_para_renderer",
        False,
    ):
        return {
            "versao": "malha_corporal_2d_v1",
            "status": "renderer_nao_liberado",
            "disponivel": False,
            "pronta_para_renderer": False,
            "renderizada": False,
        }

    pontos_origem = (
        deteccao.get(
            "pontos_corporais"
        )
        or {}
    )

    geometria_imagem = (
        deteccao.get(
            "geometria_imagem"
        )
        or {}
    )

    aspect_ratio = _numero(
        geometria_imagem.get(
            "aspect_ratio"
        )
    )

    referencia_altura = (
        deteccao.get(
            "referencia_altura_corporal"
        )
        or {}
    )

    altura_visual = _numero(
        referencia_altura.get(
            "altura_corpo_relativa"
        )
    )

    if (
        altura_visual is None
        or altura_visual <= 0
    ):
        return {
            "versao": "malha_corporal_2d_v1",
            "status": "altura_visual_indisponivel",
            "disponivel": False,
            "pronta_para_renderer": False,
            "renderizada": False,
        }

    # ======================================================
    # LANDMARKS NECESSÁRIOS
    # ======================================================

    nomes_pontos = [
        "nariz",

        "orelha_esquerda",
        "orelha_direita",

        "ombro_esquerdo",
        "ombro_direito",

        "cotovelo_esquerdo",
        "cotovelo_direito",

        "punho_esquerdo",
        "punho_direito",

        "quadril_esquerdo",
        "quadril_direito",

        "joelho_esquerdo",
        "joelho_direito",

        "tornozelo_esquerdo",
        "tornozelo_direito",

        "calcanhar_esquerdo",
        "calcanhar_direito",

        "ponta_pe_esquerdo",
        "ponta_pe_direito",
    ]

    pontos = {}

    for nome in nomes_pontos:
        pontos[nome] = (
            _extrair_ponto(
                pontos_origem,
                nome,
            )
        )

    # ======================================================
    # CENTROS ESTRUTURAIS
    # ======================================================

    centro_ombros = (
        _centro_pontos(
            pontos.get(
                "ombro_esquerdo"
            ),
            pontos.get(
                "ombro_direito"
            ),
        )
    )

    centro_quadril = (
        _centro_pontos(
            pontos.get(
                "quadril_esquerdo"
            ),
            pontos.get(
                "quadril_direito"
            ),
        )
    )

    # ======================================================
    # REFERÊNCIA VERTICAL
    # ======================================================
    #
    # O limite inferior é obtido diretamente
    # dos pontos dos pés quando disponíveis.
    #
    # Como a referência de altura corporal
    # já foi calculada anteriormente,
    # recuperamos o limite superior:
    #
    # limite_superior =
    # limite_inferior - altura_visual
    #
    # Isso evita assumir que y=0 representa
    # o topo anatômico da pessoa.
    # ======================================================

    pontos_base = [
        pontos.get(
            "ponta_pe_esquerdo"
        ),
        pontos.get(
            "ponta_pe_direito"
        ),
        pontos.get(
            "calcanhar_esquerdo"
        ),
        pontos.get(
            "calcanhar_direito"
        ),
    ]

    valores_y_base = [
        ponto["y"]
        for ponto in pontos_base
        if ponto is not None
    ]

    if not valores_y_base:
        return {
            "versao": "malha_corporal_2d_v1",
            "status": "base_corporal_indisponivel",
            "disponivel": False,
            "pronta_para_renderer": False,
            "renderizada": False,
        }

    limite_inferior = max(
        valores_y_base
    )

    limite_superior = (
        limite_inferior
        - altura_visual
    )

    # ======================================================
    # NORMALIZAÇÃO DOS PONTOS
    # ======================================================

    pontos_normalizados = {}

    for nome, ponto in pontos.items():
        pontos_normalizados[nome] = (
            _normalizar_ponto(
                ponto=ponto,
                limite_superior=(
                    limite_superior
                ),
                altura_visual=(
                    altura_visual
                ),
            )
        )

    centro_ombros_normalizado = (
        _normalizar_ponto(
            ponto=centro_ombros,
            limite_superior=(
                limite_superior
            ),
            altura_visual=(
                altura_visual
            ),
        )
    )

    centro_quadril_normalizado = (
        _normalizar_ponto(
            ponto=centro_quadril,
            limite_superior=(
                limite_superior
            ),
            altura_visual=(
                altura_visual
            ),
        )
    )

    # ======================================================
    # SEGMENTOS DA MALHA
    # ======================================================

    segmentos_definidos = [
        (
            "linha_ombros",
            "ombro_esquerdo",
            "ombro_direito",
        ),

        (
            "braco_superior_esquerdo",
            "ombro_esquerdo",
            "cotovelo_esquerdo",
        ),

        (
            "antebraco_esquerdo",
            "cotovelo_esquerdo",
            "punho_esquerdo",
        ),

        (
            "braco_superior_direito",
            "ombro_direito",
            "cotovelo_direito",
        ),

        (
            "antebraco_direito",
            "cotovelo_direito",
            "punho_direito",
        ),

        (
            "lateral_tronco_esquerda",
            "ombro_esquerdo",
            "quadril_esquerdo",
        ),

        (
            "lateral_tronco_direita",
            "ombro_direito",
            "quadril_direito",
        ),

        (
            "linha_quadril",
            "quadril_esquerdo",
            "quadril_direito",
        ),

        (
            "coxa_esquerda",
            "quadril_esquerdo",
            "joelho_esquerdo",
        ),

        (
            "perna_inferior_esquerda",
            "joelho_esquerdo",
            "tornozelo_esquerdo",
        ),

        (
            "coxa_direita",
            "quadril_direito",
            "joelho_direito",
        ),

        (
            "perna_inferior_direita",
            "joelho_direito",
            "tornozelo_direito",
        ),

        (
            "pe_esquerdo",
            "calcanhar_esquerdo",
            "ponta_pe_esquerdo",
        ),

        (
            "pe_direito",
            "calcanhar_direito",
            "ponta_pe_direito",
        ),
    ]

    segmentos = []

    for (
        nome_segmento,
        inicio,
        fim,
    ) in segmentos_definidos:

        ponto_inicio = (
            pontos_normalizados.get(
                inicio
            )
        )

        ponto_fim = (
            pontos_normalizados.get(
                fim
            )
        )

        disponivel = (
            ponto_inicio is not None
            and ponto_fim is not None
        )

        segmentos.append(
            {
                "nome": (
                    nome_segmento
                ),

                "inicio": (
                    inicio
                ),

                "fim": (
                    fim
                ),

                "disponivel": (
                    disponivel
                ),
            }
        )

    # ======================================================
    # TRONCO POLIGONAL
    # ======================================================

    nomes_tronco = [
        "ombro_esquerdo",
        "ombro_direito",
        "quadril_direito",
        "quadril_esquerdo",
    ]

    tronco_completo = all(
        pontos_normalizados.get(
            nome
        )
        is not None
        for nome in nomes_tronco
    )

    tronco_poligono = {
        "disponivel": (
            tronco_completo
        ),

        "ordem_pontos": (
            nomes_tronco
            if tronco_completo
            else []
        ),
    }

    # ======================================================
    # QUALIDADE DA MALHA
    # ======================================================

    quantidade_pontos = len(
        pontos_normalizados
    )

    pontos_disponiveis = sum(
        ponto is not None
        for ponto in (
            pontos_normalizados.values()
        )
    )

    segmentos_disponiveis = sum(
        segmento["disponivel"]
        for segmento in segmentos
    )

    total_segmentos = len(
        segmentos
    )

    percentual_pontos = (
        pontos_disponiveis
        / quantidade_pontos
        if quantidade_pontos
        else 0
    )

    percentual_segmentos = (
        segmentos_disponiveis
        / total_segmentos
        if total_segmentos
        else 0
    )

    pronta_para_renderer = (
        tronco_completo
        and percentual_pontos >= 0.80
        and percentual_segmentos >= 0.80
    )

    if pronta_para_renderer:
        status = (
            "malha_corporal_2d_pronta"
        )

    elif pontos_disponiveis > 0:
        status = (
            "malha_corporal_2d_parcial"
        )

    else:
        status = (
            "malha_corporal_2d_indisponivel"
        )

    # ======================================================
    # SAÍDA
    # ======================================================

    return {
        "versao": (
            "malha_corporal_2d_v1"
        ),

        "status": (
            status
        ),

        "disponivel": (
            pontos_disponiveis > 0
        ),

        "origem": {
            "landmarks": (
                "deteccao_humana"
            ),

            "estado_renderizacao": (
                "estado_renderizacao_avatar_v1"
            ),

            "usa_landmarks_reais": True,

            "pontos_inventados": False,
        },

        "sistema_referencia": {
            "tipo": (
                "corpo_2d_normalizado"
            ),

            "eixo_y": (
                "altura_visual_corpo"
            ),

            "topo_corpo": 0.0,

            "base_corpo": 1.0,

            "altura_corpo": 1.0,

            "eixo_x": (
                "coordenada_normalizada_imagem"
            ),

            "usa_centimetros": False,
        },

        "aspect_ratio_imagem": (
                _arredondar(
                    aspect_ratio
                )
            ),

            "correcao_horizontal_disponivel": (
                aspect_ratio is not None
                and aspect_ratio > 0
            ),

        "limites_origem": {
            "superior_y": _arredondar(
                limite_superior
            ),

            "inferior_y": _arredondar(
                limite_inferior
            ),

            "altura_visual": _arredondar(
                altura_visual
            ),
        },

        "centros_estruturais": {
            "ombros": (
                centro_ombros_normalizado
            ),

            "quadril": (
                centro_quadril_normalizado
            ),
        },

        "pontos": (
            pontos_normalizados
        ),

        "segmentos": (
            segmentos
        ),

        "tronco": (
            tronco_poligono
        ),

        "qualidade": {
            "pontos_disponiveis": (
                pontos_disponiveis
            ),

            "total_pontos": (
                quantidade_pontos
            ),

            "percentual_pontos": (
                _arredondar(
                    percentual_pontos
                )
            ),

            "segmentos_disponiveis": (
                segmentos_disponiveis
            ),

            "total_segmentos": (
                total_segmentos
            ),

            "percentual_segmentos": (
                _arredondar(
                    percentual_segmentos
                )
            ),

            "tronco_completo": (
                tronco_completo
            ),
        },

        "capacidades": {
            "desenhar_esqueleto_2d": (
                pronta_para_renderer
            ),

            "desenhar_tronco_2d": (
                tronco_completo
            ),

            "desenhar_avatar_visual": (
                pronta_para_renderer
            ),

            "vestir_produto": False,

            "simular_caimento": False,

            "gerar_avatar_3d": False,
        },

        "restricoes": {
            "altura_fisica_inferida": False,

            "medidas_cm_inferidas": False,

            "circunferencias_inferidas": False,

            "anatomia_ausente_inventada": False,

            "recomendacao_tamanho": False,
        },

        "pronta_para_renderer": (
            pronta_para_renderer
        ),

        "renderizada": False,

        "experimental": True,

        "mensagem": (
            "Malha Corporal 2D V1 preparada "
            "a partir dos landmarks reais da "
            "fotografia em espaço corporal "
            "normalizado."
        ),
    }