def _numero(
    valor,
):
    """
    Converte um valor para float
    de forma segura.
    """

    if valor is None:
        return None

    try:
        return float(
            valor
        )

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
    Arredonda valores numéricos
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


def _extrair_x(
    ponto,
):
    """
    Extrai a coordenada horizontal
    original da malha.
    """

    if not isinstance(
        ponto,
        dict,
    ):
        return None

    return _numero(
        ponto.get(
            "x_imagem"
        )
    )


def _extrair_y(
    ponto,
):
    """
    Extrai a coordenada vertical
    normalizada do corpo.
    """

    if not isinstance(
        ponto,
        dict,
    ):
        return None

    return _numero(
        ponto.get(
            "y_corpo"
        )
    )


def _normalizar_x_renderer(
    x,
    centro_corpo_x,
    aspect_ratio,
    altura_visual,
):
    """
    Centraliza e corrige horizontalmente
    o corpo no renderer.

    O eixo X é corrigido pelo aspect ratio
    da imagem e normalizado pela mesma
    altura visual usada no eixo Y.

    centro estrutural do corpo = 0.5
    altura visual do corpo = 1.0
    """

    x = _numero(
        x
    )

    centro_corpo_x = _numero(
        centro_corpo_x
    )

    aspect_ratio = _numero(
        aspect_ratio
    )

    altura_visual = _numero(
        altura_visual
    )

    if (
        x is None
        or centro_corpo_x is None
        or aspect_ratio is None
        or aspect_ratio <= 0
        or altura_visual is None
        or altura_visual <= 0
    ):
        return None

    deslocamento_corrigido = (
        (
            x
            - centro_corpo_x
        )
        * aspect_ratio
        / altura_visual
    )

    return _arredondar(
        0.5
        + deslocamento_corrigido
    )


def _converter_ponto_renderer(
    ponto,
    centro_corpo_x,
    aspect_ratio,
    altura_visual,
):
    """
    Converte um ponto da malha corporal
    para o sistema de coordenadas
    do Renderer 2D.
    """

    if not isinstance(
        ponto,
        dict,
    ):
        return None

    x = _extrair_x(
        ponto
    )

    y = _extrair_y(
        ponto
    )

    if (
        x is None
        or y is None
    ):
        return None

    x_renderer = (
        _normalizar_x_renderer(
            x=x,
            centro_corpo_x=(
                centro_corpo_x
            ),
            aspect_ratio=(
                aspect_ratio
            ),
            altura_visual=(
                altura_visual
            ),
        )
    )

    if x_renderer is None:
        return None

    return {
        "x": (
            x_renderer
        ),

        "y": (
            _arredondar(
                y
            )
        ),

        "origem": (
            "malha_corporal_2d_v1"
        ),
    }


def gerar_renderer_avatar_2d_v1(
    malha_corporal_2d: dict,
):
    """
    Prepara o Renderer do Avatar 2D V1.

    Recebe a Malha Corporal 2D V1 e
    transforma suas coordenadas para
    um espaço próprio de renderização.

    A geometria horizontal é corrigida
    utilizando o aspect ratio da imagem
    e normalizada pela altura visual
    corporal.

    IMPORTANTE:

    Esta função NÃO:
    - calcula centímetros;
    - estima altura física;
    - estima peso;
    - estima circunferências;
    - recomenda tamanho;
    - veste a roupa;
    - simula tecido;
    - gera imagem final;
    - inventa landmarks;
    - altera as etapas métricas anteriores.

    A saída representa apenas geometria
    visual proporcional pronta para desenho.
    """

    # ======================================================
    # VALIDAÇÃO DA MALHA
    # ======================================================

    if not isinstance(
        malha_corporal_2d,
        dict,
    ):
        return {
            "versao": (
                "renderer_avatar_2d_v1"
            ),

            "status": (
                "malha_invalida"
            ),

            "disponivel": False,

            "pronto": False,

            "desenhado": False,

            "imagem_gerada": False,
        }

    if not malha_corporal_2d.get(
        "pronta_para_renderer",
        False,
    ):
        return {
            "versao": (
                "renderer_avatar_2d_v1"
            ),

            "status": (
                "malha_nao_liberada"
            ),

            "disponivel": False,

            "pronto": False,

            "desenhado": False,

            "imagem_gerada": False,
        }

    # ======================================================
    # DADOS DA MALHA
    # ======================================================

    pontos_malha = (
        malha_corporal_2d.get(
            "pontos"
        )
        or {}
    )

    limites_origem = (
        malha_corporal_2d.get(
            "limites_origem"
        )
        or {}
    )

    centros = (
        malha_corporal_2d.get(
            "centros_estruturais"
        )
        or {}
    )

    # ======================================================
    # CORREÇÃO IMPORTANTE
    #
    # O aspect_ratio está diretamente
    # dentro de malha_corporal_2d.
    # ======================================================

    aspect_ratio = _numero(
        malha_corporal_2d.get(
            "aspect_ratio_imagem"
        )
    )

    altura_visual = _numero(
        limites_origem.get(
            "altura_visual"
        )
    )

    # ======================================================
    # VALIDAÇÃO DA GEOMETRIA HORIZONTAL
    # ======================================================

    if (
        aspect_ratio is None
        or aspect_ratio <= 0
    ):
        return {
            "versao": (
                "renderer_avatar_2d_v1"
            ),

            "status": (
                "aspect_ratio_indisponivel"
            ),

            "disponivel": False,

            "pronto": False,

            "desenhado": False,

            "imagem_gerada": False,
        }

    if (
        altura_visual is None
        or altura_visual <= 0
    ):
        return {
            "versao": (
                "renderer_avatar_2d_v1"
            ),

            "status": (
                "altura_visual_indisponivel"
            ),

            "disponivel": False,

            "pronto": False,

            "desenhado": False,

            "imagem_gerada": False,
        }

    fator_correcao_horizontal = (
        aspect_ratio
        / altura_visual
    )

    # ======================================================
    # CENTROS ESTRUTURAIS
    # ======================================================

    centro_ombros = (
        centros.get(
            "ombros"
        )
        or {}
    )

    centro_quadril = (
        centros.get(
            "quadril"
        )
        or {}
    )

    centro_ombros_x = (
        _extrair_x(
            centro_ombros
        )
    )

    centro_quadril_x = (
        _extrair_x(
            centro_quadril
        )
    )

    centros_validos = [
        valor
        for valor in (
            centro_ombros_x,
            centro_quadril_x,
        )
        if valor is not None
    ]

    if not centros_validos:
        return {
            "versao": (
                "renderer_avatar_2d_v1"
            ),

            "status": (
                "centro_corporal_indisponivel"
            ),

            "disponivel": False,

            "pronto": False,

            "desenhado": False,

            "imagem_gerada": False,
        }

    centro_corpo_x = (
        sum(
            centros_validos
        )
        / len(
            centros_validos
        )
    )

    centro_corpo_x = (
        _arredondar(
            centro_corpo_x
        )
    )

    # ======================================================
    # CONVERSÃO DOS PONTOS
    # ======================================================

    pontos_renderer = {}

    for (
        nome,
        ponto,
    ) in pontos_malha.items():

        pontos_renderer[
            nome
        ] = (
            _converter_ponto_renderer(
                ponto=ponto,
                centro_corpo_x=(
                    centro_corpo_x
                ),
                aspect_ratio=(
                    aspect_ratio
                ),
                altura_visual=(
                    altura_visual
                ),
            )
        )

    # ======================================================
    # CONVERSÃO DOS CENTROS
    # ======================================================

    centro_ombros_renderer = (
        _converter_ponto_renderer(
            ponto=centro_ombros,
            centro_corpo_x=(
                centro_corpo_x
            ),
            aspect_ratio=(
                aspect_ratio
            ),
            altura_visual=(
                altura_visual
            ),
        )
    )

    centro_quadril_renderer = (
        _converter_ponto_renderer(
            ponto=centro_quadril,
            centro_corpo_x=(
                centro_corpo_x
            ),
            aspect_ratio=(
                aspect_ratio
            ),
            altura_visual=(
                altura_visual
            ),
        )
    )

    # ======================================================
    # SEGMENTOS
    # ======================================================

    segmentos_origem = (
        malha_corporal_2d.get(
            "segmentos"
        )
        or []
    )

    segmentos_renderer = []

    for segmento in segmentos_origem:

        if not isinstance(
            segmento,
            dict,
        ):
            continue

        inicio_nome = (
            segmento.get(
                "inicio"
            )
        )

        fim_nome = (
            segmento.get(
                "fim"
            )
        )

        inicio = (
            pontos_renderer.get(
                inicio_nome
            )
        )

        fim = (
            pontos_renderer.get(
                fim_nome
            )
        )

        disponivel = (
            bool(
                segmento.get(
                    "disponivel",
                    False,
                )
            )
            and inicio is not None
            and fim is not None
        )

        segmentos_renderer.append(
            {
                "nome": (
                    segmento.get(
                        "nome"
                    )
                ),

                "inicio": (
                    inicio_nome
                ),

                "fim": (
                    fim_nome
                ),

                "disponivel": (
                    disponivel
                ),
            }
        )

    # ======================================================
    # FORMA DO TRONCO
    # ======================================================

    pontos_tronco = [
        "ombro_esquerdo",
        "ombro_direito",
        "quadril_direito",
        "quadril_esquerdo",
    ]

    tronco_disponivel = all(
        pontos_renderer.get(
            nome
        )
        is not None
        for nome in pontos_tronco
    )

    forma_tronco = {
        "tipo": (
            "poligono"
        ),

        "disponivel": (
            tronco_disponivel
        ),

        "pontos": (
            pontos_tronco
            if tronco_disponivel
            else []
        ),
    }

    # ======================================================
    # BRAÇOS
    # ======================================================

    bracos = {
        "esquerdo": {
            "tipo": (
                "linha_articulada"
            ),

            "pontos": [
                "ombro_esquerdo",
                "cotovelo_esquerdo",
                "punho_esquerdo",
            ],

            "disponivel": all(
                pontos_renderer.get(
                    nome
                )
                is not None
                for nome in (
                    "ombro_esquerdo",
                    "cotovelo_esquerdo",
                    "punho_esquerdo",
                )
            ),
        },

        "direito": {
            "tipo": (
                "linha_articulada"
            ),

            "pontos": [
                "ombro_direito",
                "cotovelo_direito",
                "punho_direito",
            ],

            "disponivel": all(
                pontos_renderer.get(
                    nome
                )
                is not None
                for nome in (
                    "ombro_direito",
                    "cotovelo_direito",
                    "punho_direito",
                )
            ),
        },
    }

    # ======================================================
    # PERNAS
    # ======================================================

    pernas = {
        "esquerda": {
            "tipo": (
                "linha_articulada"
            ),

            "pontos": [
                "quadril_esquerdo",
                "joelho_esquerdo",
                "tornozelo_esquerdo",
            ],

            "disponivel": all(
                pontos_renderer.get(
                    nome
                )
                is not None
                for nome in (
                    "quadril_esquerdo",
                    "joelho_esquerdo",
                    "tornozelo_esquerdo",
                )
            ),
        },

        "direita": {
            "tipo": (
                "linha_articulada"
            ),

            "pontos": [
                "quadril_direito",
                "joelho_direito",
                "tornozelo_direito",
            ],

            "disponivel": all(
                pontos_renderer.get(
                    nome
                )
                is not None
                for nome in (
                    "quadril_direito",
                    "joelho_direito",
                    "tornozelo_direito",
                )
            ),
        },
    }

    # ======================================================
    # PÉS
    # ======================================================

    pes = {
        "esquerdo": {
            "tipo": (
                "segmento"
            ),

            "pontos": [
                "calcanhar_esquerdo",
                "ponta_pe_esquerdo",
            ],

            "disponivel": all(
                pontos_renderer.get(
                    nome
                )
                is not None
                for nome in (
                    "calcanhar_esquerdo",
                    "ponta_pe_esquerdo",
                )
            ),
        },

        "direito": {
            "tipo": (
                "segmento"
            ),

            "pontos": [
                "calcanhar_direito",
                "ponta_pe_direito",
            ],

            "disponivel": all(
                pontos_renderer.get(
                    nome
                )
                is not None
                for nome in (
                    "calcanhar_direito",
                    "ponta_pe_direito",
                )
            ),
        },
    }

    # ======================================================
    # QUALIDADE DOS PONTOS
    # ======================================================

    total_pontos = len(
        pontos_renderer
    )

    pontos_disponiveis = sum(
        ponto is not None
        for ponto in (
            pontos_renderer.values()
        )
    )

    total_segmentos = len(
        segmentos_renderer
    )

    segmentos_disponiveis = sum(
        segmento.get(
            "disponivel",
            False,
        )
        for segmento in (
            segmentos_renderer
        )
    )

    percentual_pontos = (
        pontos_disponiveis
        / total_pontos
        if total_pontos
        else 0
    )

    percentual_segmentos = (
        segmentos_disponiveis
        / total_segmentos
        if total_segmentos
        else 0
    )

    # ======================================================
    # VALIDAÇÕES PROPORCIONAIS
    # ======================================================

    ombro_esquerdo = (
        pontos_renderer.get(
            "ombro_esquerdo"
        )
    )

    ombro_direito = (
        pontos_renderer.get(
            "ombro_direito"
        )
    )

    quadril_esquerdo = (
        pontos_renderer.get(
            "quadril_esquerdo"
        )
    )

    quadril_direito = (
        pontos_renderer.get(
            "quadril_direito"
        )
    )

    largura_ombros_renderer = None
    largura_quadril_renderer = None

    if (
        ombro_esquerdo is not None
        and ombro_direito is not None
    ):
        largura_ombros_renderer = (
            abs(
                ombro_esquerdo[
                    "x"
                ]
                - ombro_direito[
                    "x"
                ]
            )
        )

        largura_ombros_renderer = (
            _arredondar(
                largura_ombros_renderer
            )
        )

    if (
        quadril_esquerdo is not None
        and quadril_direito is not None
    ):
        largura_quadril_renderer = (
            abs(
                quadril_esquerdo[
                    "x"
                ]
                - quadril_direito[
                    "x"
                ]
            )
        )

        largura_quadril_renderer = (
            _arredondar(
                largura_quadril_renderer
            )
        )

    # ======================================================
    # STATUS FINAL
    # ======================================================

    renderer_pronto = (
        tronco_disponivel
        and percentual_pontos >= 0.80
        and percentual_segmentos >= 0.80
    )

    if renderer_pronto:
        status = (
            "renderer_avatar_2d_pronto"
        )

    elif pontos_disponiveis > 0:
        status = (
            "renderer_avatar_2d_parcial"
        )

    else:
        status = (
            "renderer_avatar_2d_indisponivel"
        )

    # ======================================================
    # SAÍDA
    # ======================================================

    return {
        "versao": (
            "renderer_avatar_2d_v1"
        ),

        "status": (
            status
        ),

        "disponivel": (
            pontos_disponiveis > 0
        ),

        "origem": (
            "malha_corporal_2d_v1"
        ),

        "canvas_normalizado": {
            "largura": 1.0,

            "altura": 1.0,

            "centro_x": 0.5,

            "topo_y": 0.0,

            "base_y": 1.0,

            "unidade": (
                "coordenada_normalizada_renderer"
            ),
        },

        "centralizacao": {
            "centro_corpo_origem_x": (
                centro_corpo_x
            ),

            "centro_renderer_x": 0.5,

            "aplicada": True,

            "preserva_geometria_relativa": True,

            "aspect_ratio_aplicado": (
                _arredondar(
                    aspect_ratio
                )
            ),

            "altura_visual_referencia": (
                _arredondar(
                    altura_visual
                )
            ),

            "fator_correcao_horizontal": (
                _arredondar(
                    fator_correcao_horizontal
                )
            ),

            "correcao_horizontal_aplicada": True,

            "sistema_horizontal": (
                "proporcao_da_altura_visual"
            ),
        },

        "centros_estruturais": {
            "ombros": (
                centro_ombros_renderer
            ),

            "quadril": (
                centro_quadril_renderer
            ),
        },

        "pontos": (
            pontos_renderer
        ),

        "segmentos": (
            segmentos_renderer
        ),

        "formas": {
            "tronco": (
                forma_tronco
            ),

            "bracos": (
                bracos
            ),

            "pernas": (
                pernas
            ),

            "pes": (
                pes
            ),
        },

        "validacao_proporcional": {
            "largura_ombros_renderer": (
                largura_ombros_renderer
            ),

            "largura_quadril_renderer": (
                largura_quadril_renderer
            ),

            "referencia": (
                "altura_visual_corpo_1_0"
            ),

            "usa_medida_fisica": False,
        },

        "qualidade": {
            "pontos_disponiveis": (
                pontos_disponiveis
            ),

            "total_pontos": (
                total_pontos
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

            "tronco_disponivel": (
                tronco_disponivel
            ),
        },

        "capacidades": {
            "avatar_2d_desenhavel": (
                renderer_pronto
            ),

            "tronco_desenhavel": (
                tronco_disponivel
            ),

            "bracos_desenhaveis": (
                bracos[
                    "esquerdo"
                ][
                    "disponivel"
                ]
                and bracos[
                    "direito"
                ][
                    "disponivel"
                ]
            ),

            "pernas_desenhaveis": (
                pernas[
                    "esquerda"
                ][
                    "disponivel"
                ]
                and pernas[
                    "direita"
                ][
                    "disponivel"
                ]
            ),

            "produto_aplicavel": False,

            "imagem_final_geravel": False,
        },

        "restricoes": {
            "usa_centimetros": False,

            "estima_altura_fisica": False,

            "estima_peso": False,

            "estima_circunferencias": False,

            "inventa_anatomia": False,

            "recomenda_tamanho": False,
        },

        "pronto": (
            renderer_pronto
        ),

        "desenhado": False,

        "imagem_gerada": False,

        "experimental": True,

        "mensagem": (
            "Renderer do Avatar 2D V1 preparado "
            "com coordenadas corporais centralizadas "
            "e correção horizontal baseada no aspect "
            "ratio da imagem e na altura visual corporal."
        ),
    }