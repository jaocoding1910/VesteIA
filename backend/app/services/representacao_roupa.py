from app.services.categorias_vestuario import (
    normalizar_categoria,
    obter_familia_categoria,
)


def _numero(
    valor,
):
    """
    Converte valor para float
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


# ==========================================================
# TEMPLATE SUPERIOR
# ==========================================================

def _gerar_template_superior(
    largura_relativa,
    categoria,
):
    """
    Template visual base para peças superiores.

    Utilizado por:
    - camiseta;
    - camisa;
    - regata;
    - jaqueta;
    - casaco.

    Não representa molde industrial.
    """

    if (
        largura_relativa is None
        or largura_relativa <= 0
    ):
        return None

    centro_x = 0.5

    metade_largura = (
        largura_relativa
        / 2
    )

    lateral_esquerda = (
        centro_x
        - metade_largura
    )

    lateral_direita = (
        centro_x
        + metade_largura
    )

    y_topo = 0.0
    y_ombros = 0.08
    y_axilas = 0.24
    y_barra = 1.0

    # ======================================================
    # COMPRIMENTO VISUAL DAS MANGAS
    # ======================================================

    if categoria == "regata":
        extensao_manga = (
            largura_relativa
            * 0.03
        )

        queda_manga = 0.16

    elif categoria in {
        "jaqueta",
        "casaco",
    }:
        extensao_manga = (
            largura_relativa
            * 0.22
        )

        queda_manga = 0.34

    elif categoria == "camisa":
        extensao_manga = (
            largura_relativa
            * 0.20
        )

        queda_manga = 0.29

    else:
        extensao_manga = (
            largura_relativa
            * 0.18
        )

        queda_manga = 0.22

    largura_gola = (
        largura_relativa
        * 0.26
    )

    metade_gola = (
        largura_gola
        / 2
    )

    gola_esquerda = (
        centro_x
        - metade_gola
    )

    gola_direita = (
        centro_x
        + metade_gola
    )

    return {
        "tipo": (
            f"template_{categoria}_2d"
        ),

        "familia": (
            "superior"
        ),

        "categoria": (
            categoria
        ),

        "centro_x": (
            _arredondar(
                centro_x
            )
        ),

        "pontos": {
            "gola_esquerda": {
                "x": (
                    _arredondar(
                        gola_esquerda
                    )
                ),
                "y": 0.0,
            },

            "gola_direita": {
                "x": (
                    _arredondar(
                        gola_direita
                    )
                ),
                "y": 0.0,
            },

            "ombro_esquerdo": {
                "x": (
                    _arredondar(
                        lateral_esquerda
                    )
                ),
                "y": (
                    _arredondar(
                        y_ombros
                    )
                ),
            },

            "ombro_direito": {
                "x": (
                    _arredondar(
                        lateral_direita
                    )
                ),
                "y": (
                    _arredondar(
                        y_ombros
                    )
                ),
            },

            "manga_esquerda_externa": {
                "x": (
                    _arredondar(
                        lateral_esquerda
                        - extensao_manga
                    )
                ),
                "y": (
                    _arredondar(
                        queda_manga
                    )
                ),
            },

            "manga_direita_externa": {
                "x": (
                    _arredondar(
                        lateral_direita
                        + extensao_manga
                    )
                ),
                "y": (
                    _arredondar(
                        queda_manga
                    )
                ),
            },

            "axila_esquerda": {
                "x": (
                    _arredondar(
                        lateral_esquerda
                    )
                ),
                "y": (
                    _arredondar(
                        y_axilas
                    )
                ),
            },

            "axila_direita": {
                "x": (
                    _arredondar(
                        lateral_direita
                    )
                ),
                "y": (
                    _arredondar(
                        y_axilas
                    )
                ),
            },

            "barra_esquerda": {
                "x": (
                    _arredondar(
                        lateral_esquerda
                    )
                ),
                "y": (
                    _arredondar(
                        y_barra
                    )
                ),
            },

            "barra_direita": {
                "x": (
                    _arredondar(
                        lateral_direita
                    )
                ),
                "y": (
                    _arredondar(
                        y_barra
                    )
                ),
            },
        },

        "regioes": {
            "tronco": {
                "tipo": "poligono",

                "pontos": [
                    "ombro_esquerdo",
                    "ombro_direito",
                    "axila_direita",
                    "barra_direita",
                    "barra_esquerda",
                    "axila_esquerda",
                ],
            },

            "manga_esquerda": {
                "tipo": (
                    "regiao_visual"
                ),

                "pontos": [
                    "ombro_esquerdo",
                    "manga_esquerda_externa",
                    "axila_esquerda",
                ],
            },

            "manga_direita": {
                "tipo": (
                    "regiao_visual"
                ),

                "pontos": [
                    "ombro_direito",
                    "manga_direita_externa",
                    "axila_direita",
                ],
            },

            "gola": {
                "tipo": (
                    "abertura_visual"
                ),

                "pontos": [
                    "gola_esquerda",
                    "gola_direita",
                ],
            },
        },

        "referencias": {
            "topo_y": (
                _arredondar(
                    y_topo
                )
            ),

            "linha_ombros_y": (
                _arredondar(
                    y_ombros
                )
            ),

            "linha_axilas_y": (
                _arredondar(
                    y_axilas
                )
            ),

            "barra_y": (
                _arredondar(
                    y_barra
                )
            ),
        },
    }


# ==========================================================
# TEMPLATE INFERIOR
# ==========================================================

def _gerar_template_inferior(
    largura_relativa,
    categoria,
):
    """
    Template visual base para peças inferiores.

    Utilizado por:
    - calça;
    - short;
    - bermuda;
    - saia.
    """

    if (
        largura_relativa is None
        or largura_relativa <= 0
    ):
        return None

    centro_x = 0.5

    metade_largura = (
        largura_relativa
        / 2
    )

    cintura_esquerda_x = (
        centro_x
        - metade_largura
    )

    cintura_direita_x = (
        centro_x
        + metade_largura
    )

    y_cintura = 0.0
    y_quadril = 0.12

    if categoria == "short":
        y_entrepernas = 0.38
        y_joelho = 0.58
        y_barra = 0.62

    elif categoria == "bermuda":
        y_entrepernas = 0.32
        y_joelho = 0.66
        y_barra = 0.74

    elif categoria == "saia":
        y_entrepernas = None
        y_joelho = None
        y_barra = 0.72

    else:
        y_entrepernas = 0.30
        y_joelho = 0.60
        y_barra = 1.0

    expansao_quadril = (
        largura_relativa
        * 0.035
    )

    quadril_esquerdo_x = (
        cintura_esquerda_x
        - expansao_quadril
    )

    quadril_direito_x = (
        cintura_direita_x
        + expansao_quadril
    )

    # ======================================================
    # SAIA
    # ======================================================

    if categoria == "saia":

        abertura_barra = (
            largura_relativa
            * 0.12
        )

        return {
            "tipo": (
                "template_saia_2d"
            ),

            "familia": (
                "inferior"
            ),

            "categoria": (
                categoria
            ),

            "centro_x": 0.5,

            "pontos": {
                "cintura_esquerda": {
                    "x": (
                        _arredondar(
                            cintura_esquerda_x
                        )
                    ),
                    "y": 0.0,
                },

                "cintura_direita": {
                    "x": (
                        _arredondar(
                            cintura_direita_x
                        )
                    ),
                    "y": 0.0,
                },

                "quadril_esquerdo": {
                    "x": (
                        _arredondar(
                            quadril_esquerdo_x
                        )
                    ),
                    "y": 0.12,
                },

                "quadril_direito": {
                    "x": (
                        _arredondar(
                            quadril_direito_x
                        )
                    ),
                    "y": 0.12,
                },

                "barra_esquerda": {
                    "x": (
                        _arredondar(
                            quadril_esquerdo_x
                            - abertura_barra
                        )
                    ),
                    "y": (
                        _arredondar(
                            y_barra
                        )
                    ),
                },

                "barra_direita": {
                    "x": (
                        _arredondar(
                            quadril_direito_x
                            + abertura_barra
                        )
                    ),
                    "y": (
                        _arredondar(
                            y_barra
                        )
                    ),
                },
            },

            "regioes": {
                "saia": {
                    "tipo": (
                        "poligono"
                    ),

                    "pontos": [
                        "cintura_esquerda",
                        "cintura_direita",
                        "quadril_direito",
                        "barra_direita",
                        "barra_esquerda",
                        "quadril_esquerdo",
                    ],
                },
            },

            "referencias": {
                "linha_cintura_y": 0.0,
                "linha_quadril_y": 0.12,
                "barra_y": (
                    _arredondar(
                        y_barra
                    )
                ),
            },
        }

    # ======================================================
    # CALÇA / SHORT / BERMUDA
    # ======================================================

    entrepernas_x = (
        centro_x
    )

    largura_perna_joelho = (
        largura_relativa
        * 0.29
    )

    largura_perna_barra = (
        largura_relativa
        * 0.22
    )

    deslocamento_centro_perna = (
        largura_relativa
        * 0.23
    )

    centro_perna_esquerda = (
        centro_x
        - deslocamento_centro_perna
    )

    centro_perna_direita = (
        centro_x
        + deslocamento_centro_perna
    )

    metade_joelho = (
        largura_perna_joelho
        / 2
    )

    joelho_esquerdo_externo_x = (
        centro_perna_esquerda
        - metade_joelho
    )

    joelho_esquerdo_interno_x = (
        centro_perna_esquerda
        + metade_joelho
    )

    joelho_direito_interno_x = (
        centro_perna_direita
        - metade_joelho
    )

    joelho_direito_externo_x = (
        centro_perna_direita
        + metade_joelho
    )

    metade_barra = (
        largura_perna_barra
        / 2
    )

    barra_esquerda_externa_x = (
        centro_perna_esquerda
        - metade_barra
    )

    barra_esquerda_interna_x = (
        centro_perna_esquerda
        + metade_barra
    )

    barra_direita_interna_x = (
        centro_perna_direita
        - metade_barra
    )

    barra_direita_externa_x = (
        centro_perna_direita
        + metade_barra
    )

    return {
        "tipo": (
            f"template_{categoria}_2d"
        ),

        "familia": (
            "inferior"
        ),

        "categoria": (
            categoria
        ),

        "centro_x": (
            _arredondar(
                centro_x
            )
        ),

        "pontos": {
            "cintura_esquerda": {
                "x": (
                    _arredondar(
                        cintura_esquerda_x
                    )
                ),
                "y": 0.0,
            },

            "cintura_direita": {
                "x": (
                    _arredondar(
                        cintura_direita_x
                    )
                ),
                "y": 0.0,
            },

            "quadril_esquerdo": {
                "x": (
                    _arredondar(
                        quadril_esquerdo_x
                    )
                ),
                "y": 0.12,
            },

            "quadril_direito": {
                "x": (
                    _arredondar(
                        quadril_direito_x
                    )
                ),
                "y": 0.12,
            },

            "entrepernas": {
                "x": (
                    _arredondar(
                        entrepernas_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_entrepernas
                    )
                ),
            },

            "joelho_esquerdo_externo": {
                "x": (
                    _arredondar(
                        joelho_esquerdo_externo_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_joelho
                    )
                ),
            },

            "joelho_esquerdo_interno": {
                "x": (
                    _arredondar(
                        joelho_esquerdo_interno_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_joelho
                    )
                ),
            },

            "joelho_direito_interno": {
                "x": (
                    _arredondar(
                        joelho_direito_interno_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_joelho
                    )
                ),
            },

            "joelho_direito_externo": {
                "x": (
                    _arredondar(
                        joelho_direito_externo_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_joelho
                    )
                ),
            },

            "barra_esquerda_externa": {
                "x": (
                    _arredondar(
                        barra_esquerda_externa_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_barra
                    )
                ),
            },

            "barra_esquerda_interna": {
                "x": (
                    _arredondar(
                        barra_esquerda_interna_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_barra
                    )
                ),
            },

            "barra_direita_interna": {
                "x": (
                    _arredondar(
                        barra_direita_interna_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_barra
                    )
                ),
            },

            "barra_direita_externa": {
                "x": (
                    _arredondar(
                        barra_direita_externa_x
                    )
                ),
                "y": (
                    _arredondar(
                        y_barra
                    )
                ),
            },
        },

        "regioes": {
            "cintura_quadril": {
                "tipo": "poligono",

                "pontos": [
                    "cintura_esquerda",
                    "cintura_direita",
                    "quadril_direito",
                    "entrepernas",
                    "quadril_esquerdo",
                ],
            },

            "perna_esquerda": {
                "tipo": "poligono",

                "pontos": [
                    "quadril_esquerdo",
                    "entrepernas",
                    "joelho_esquerdo_interno",
                    "barra_esquerda_interna",
                    "barra_esquerda_externa",
                    "joelho_esquerdo_externo",
                ],
            },

            "perna_direita": {
                "tipo": "poligono",

                "pontos": [
                    "quadril_direito",
                    "joelho_direito_externo",
                    "barra_direita_externa",
                    "barra_direita_interna",
                    "joelho_direito_interno",
                    "entrepernas",
                ],
            },
        },

        "referencias": {
            "linha_cintura_y": 0.0,

            "linha_quadril_y": 0.12,

            "linha_entrepernas_y": (
                _arredondar(
                    y_entrepernas
                )
            ),

            "linha_joelhos_y": (
                _arredondar(
                    y_joelho
                )
            ),

            "barra_y": (
                _arredondar(
                    y_barra
                )
            ),
        },
    }


# ==========================================================
# TEMPLATE CORPO INTEGRADO
# ==========================================================

def _gerar_template_corpo_integrado(
    largura_relativa,
    categoria,
):
    """
    Template base para:
    - vestido;
    - macacão.
    """

    if (
        largura_relativa is None
        or largura_relativa <= 0
    ):
        return None

    centro_x = 0.5

    metade_largura = (
        largura_relativa
        / 2
    )

    lateral_esquerda = (
        centro_x
        - metade_largura
    )

    lateral_direita = (
        centro_x
        + metade_largura
    )

    largura_gola = (
        largura_relativa
        * 0.24
    )

    metade_gola = (
        largura_gola
        / 2
    )

    largura_quadril = (
        largura_relativa
        * 0.46
    )

    metade_quadril = (
        largura_quadril
        / 2
    )

    abertura_barra = (
        largura_relativa
        * (
            0.20
            if categoria == "vestido"
            else 0.06
        )
    )

    return {
        "tipo": (
            f"template_{categoria}_2d"
        ),

        "familia": (
            "corpo_integrado"
        ),

        "categoria": (
            categoria
        ),

        "centro_x": 0.5,

        "pontos": {
            "gola_esquerda": {
                "x": (
                    _arredondar(
                        centro_x
                        - metade_gola
                    )
                ),
                "y": 0.0,
            },

            "gola_direita": {
                "x": (
                    _arredondar(
                        centro_x
                        + metade_gola
                    )
                ),
                "y": 0.0,
            },

            "ombro_esquerdo": {
                "x": (
                    _arredondar(
                        lateral_esquerda
                    )
                ),
                "y": 0.08,
            },

            "ombro_direito": {
                "x": (
                    _arredondar(
                        lateral_direita
                    )
                ),
                "y": 0.08,
            },

            "cintura_esquerda": {
                "x": (
                    _arredondar(
                        centro_x
                        - largura_relativa
                        * 0.38
                    )
                ),
                "y": 0.42,
            },

            "cintura_direita": {
                "x": (
                    _arredondar(
                        centro_x
                        + largura_relativa
                        * 0.38
                    )
                ),
                "y": 0.42,
            },

            "quadril_esquerdo": {
                "x": (
                    _arredondar(
                        centro_x
                        - metade_quadril
                    )
                ),
                "y": 0.56,
            },

            "quadril_direito": {
                "x": (
                    _arredondar(
                        centro_x
                        + metade_quadril
                    )
                ),
                "y": 0.56,
            },

            "barra_esquerda": {
                "x": (
                    _arredondar(
                        centro_x
                        - metade_quadril
                        - abertura_barra
                    )
                ),
                "y": 1.0,
            },

            "barra_direita": {
                "x": (
                    _arredondar(
                        centro_x
                        + metade_quadril
                        + abertura_barra
                    )
                ),
                "y": 1.0,
            },
        },

        "regioes": {
            "corpo_integrado": {
                "tipo": (
                    "poligono"
                ),

                "pontos": [
                    "ombro_esquerdo",
                    "ombro_direito",
                    "cintura_direita",
                    "quadril_direito",
                    "barra_direita",
                    "barra_esquerda",
                    "quadril_esquerdo",
                    "cintura_esquerda",
                ],
            },

            "gola": {
                "tipo": (
                    "abertura_visual"
                ),

                "pontos": [
                    "gola_esquerda",
                    "gola_direita",
                ],
            },
        },

        "referencias": {
            "linha_ombros_y": 0.08,
            "linha_cintura_y": 0.42,
            "linha_quadril_y": 0.56,
            "barra_y": 1.0,
        },
    }


# ==========================================================
# TEMPLATE CALÇADO
# ==========================================================

def _gerar_template_calcado(
    largura_relativa,
    categoria,
):
    """
    Template simplificado para calçados.

    É apenas uma representação visual 2D.
    """

    if (
        largura_relativa is None
        or largura_relativa <= 0
    ):
        return None

    centro_x = 0.5

    largura_visual = min(
        largura_relativa,
        0.65,
    )

    metade = (
        largura_visual
        / 2
    )

    return {
        "tipo": (
            f"template_{categoria}_2d"
        ),

        "familia": (
            "calcado"
        ),

        "categoria": (
            categoria
        ),

        "centro_x": (
            centro_x
        ),

        "pontos": {
            "calcanhar_esquerdo": {
                "x": (
                    _arredondar(
                        centro_x
                        - metade
                    )
                ),
                "y": 0.35,
            },

            "calcanhar_direito": {
                "x": (
                    _arredondar(
                        centro_x
                        + metade
                    )
                ),
                "y": 0.35,
            },

            "ponta_esquerda": {
                "x": (
                    _arredondar(
                        centro_x
                        - metade
                        * 0.85
                    )
                ),
                "y": 1.0,
            },

            "ponta_direita": {
                "x": (
                    _arredondar(
                        centro_x
                        + metade
                        * 0.85
                    )
                ),
                "y": 1.0,
            },
        },

        "regioes": {
            "calcado": {
                "tipo": (
                    "poligono"
                ),

                "pontos": [
                    "calcanhar_esquerdo",
                    "calcanhar_direito",
                    "ponta_direita",
                    "ponta_esquerda",
                ],
            },
        },

        "referencias": {
            "calcanhar_y": 0.35,
            "ponta_y": 1.0,
        },
    }


# ==========================================================
# REPRESENTAÇÃO PRINCIPAL
# ==========================================================

def gerar_representacao_roupa_v1(
    produto: dict,
):
    """
    Gera a Representação da Roupa V1.

    Sprint Multivestimenta.

    A função transforma os dados cadastrados
    da peça em uma representação visual
    proporcional própria.

    IMPORTANTE:

    Esta função NÃO:
    - mede o corpo;
    - converte corpo para centímetros;
    - compara cm da peça com corpo;
    - recomenda tamanho;
    - veste o avatar;
    - simula tecido;
    - gera imagem final.
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if not isinstance(
        produto,
        dict,
    ):
        return {
            "versao": (
                "representacao_roupa_v1"
            ),

            "status": (
                "produto_invalido"
            ),

            "disponivel": False,

            "pronta_para_vestir_avatar": False,
        }

    categoria_original = (
        produto.get(
            "categoria"
        )
    )

    categoria = (
        normalizar_categoria(
            categoria_original
        )
    )

    familia = (
        obter_familia_categoria(
            categoria
        )
        if categoria
        else None
    )

    if categoria is None:
        return {
            "versao": (
                "representacao_roupa_v1"
            ),

            "status": (
                "categoria_nao_implementada"
            ),

            "disponivel": False,

            "categoria": None,

            "categoria_original": (
                categoria_original
            ),

            "familia": None,

            "pronta_para_vestir_avatar": False,

            "mensagem": (
                "A categoria da peça ainda não "
                "é reconhecida pelo VesteIA."
            ),
        }

    largura_cm = (
        _numero(
            produto.get(
                "largura_cm"
            )
        )
    )

    comprimento_cm = (
        _numero(
            produto.get(
                "comprimento_cm"
            )
        )
    )

    modelagem = (
        produto.get(
            "modelagem"
        )
    )

    # ======================================================
    # DIMENSÕES DA PEÇA
    # ======================================================

    if (
        largura_cm is None
        or largura_cm <= 0
        or comprimento_cm is None
        or comprimento_cm <= 0
    ):
        return {
            "versao": (
                "representacao_roupa_v1"
            ),

            "status": (
                "dimensoes_peca_indisponiveis"
            ),

            "disponivel": False,

            "categoria": (
                categoria
            ),

            "familia": (
                familia
            ),

            "pronta_para_vestir_avatar": False,

            "mensagem": (
                "A peça não possui largura e "
                "comprimento válidos para gerar "
                "uma representação visual proporcional."
            ),
        }

    altura_normalizada = 1.0

    largura_normalizada = (
        largura_cm
        / comprimento_cm
    )

    largura_normalizada = (
        _arredondar(
            largura_normalizada
        )
    )

    # ======================================================
    # TEMPLATE POR FAMÍLIA
    # ======================================================

    template = None

    if familia == "superior":
        template = (
            _gerar_template_superior(
                largura_relativa=(
                    largura_normalizada
                ),
                categoria=(
                    categoria
                ),
            )
        )

    elif familia == "inferior":
        template = (
            _gerar_template_inferior(
                largura_relativa=(
                    largura_normalizada
                ),
                categoria=(
                    categoria
                ),
            )
        )

    elif familia == "corpo_integrado":
        template = (
            _gerar_template_corpo_integrado(
                largura_relativa=(
                    largura_normalizada
                ),
                categoria=(
                    categoria
                ),
            )
        )

    elif familia == "calcado":
        template = (
            _gerar_template_calcado(
                largura_relativa=(
                    largura_normalizada
                ),
                categoria=(
                    categoria
                ),
            )
        )

    if template is None:
        return {
            "versao": (
                "representacao_roupa_v1"
            ),

            "status": (
                "template_indisponivel"
            ),

            "disponivel": False,

            "categoria": (
                categoria
            ),

            "familia": (
                familia
            ),

            "pronta_para_vestir_avatar": False,

            "mensagem": (
                "A categoria foi reconhecida, "
                "mas ainda não possui template visual."
            ),
        }

    # ======================================================
    # SAÍDA
    # ======================================================

    return {
        "versao": (
            "representacao_roupa_v1"
        ),

        "status": (
            "representacao_roupa_pronta"
        ),

        "disponivel": True,

        "origem": (
            "dados_produto"
        ),

        "categoria": (
            categoria
        ),

        "familia": (
            familia
        ),

        "produto": {
            "id": (
                produto.get(
                    "id"
                )
            ),

            "nome": (
                produto.get(
                    "nome"
                )
            ),

            "categoria": (
                categoria
            ),

            "categoria_original": (
                categoria_original
            ),

            "familia": (
                familia
            ),

            "tamanho": (
                produto.get(
                    "tamanho"
                )
            ),

            "cor": (
                produto.get(
                    "cor"
                )
            ),

            "modelagem": (
                modelagem
            ),
        },

        "dimensoes_origem": {
            "largura_cm": (
                _arredondar(
                    largura_cm
                )
            ),

            "comprimento_cm": (
                _arredondar(
                    comprimento_cm
                )
            ),

            "unidade": (
                "cm"
            ),

            "pertencem_a": (
                "produto"
            ),
        },

        "sistema_referencia": {
            "tipo": (
                "roupa_2d_normalizada"
            ),

            "altura_roupa": (
                altura_normalizada
            ),

            "largura_roupa": (
                largura_normalizada
            ),

            "centro_horizontal": 0.5,

            "topo_y": 0.0,

            "base_y": 1.0,

            "unidade": (
                "proporcao_do_comprimento_da_peca"
            ),

            "escala_corporal": False,
        },

        "proporcoes": {
            "largura_comprimento": (
                largura_normalizada
            ),

            "altura_normalizada": (
                altura_normalizada
            ),

            "largura_normalizada": (
                largura_normalizada
            ),
        },

        "template": (
            template
        ),

        "capacidades": {
            "desenhavel_2d": True,

            "posicionavel_no_avatar": True,

            "multivestimenta": True,

            "vestir_avatar": False,

            "simular_caimento": False,

            "gerar_imagem_final": False,
        },

        "restricoes": {
            "mede_corpo": False,

            "usa_cm_do_produto_como_cm_do_corpo": False,

            "infere_medidas_corporais": False,

            "recomenda_tamanho": False,

            "simula_tecido": False,

            "representa_molde_industrial_exato": False,
        },

        "pronta_para_vestir_avatar": True,

        "vestida_no_avatar": False,

        "experimental": True,

        "mensagem": (
            "Representação da Roupa V1 gerada "
            "pela arquitetura multivestimenta "
            "do VesteIA."
        ),
    }