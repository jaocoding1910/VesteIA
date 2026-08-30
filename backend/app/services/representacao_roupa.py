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


def _normalizar_categoria(
    categoria,
):
    """
    Normaliza o nome da categoria
    para uso interno.
    """

    if not isinstance(
        categoria,
        str,
    ):
        return None

    categoria = (
        categoria
        .strip()
        .lower()
    )

    mapa = {
        "camiseta": "camiseta",
        "camisetas": "camiseta",
        "t-shirt": "camiseta",
        "tshirt": "camiseta",
    }

    return mapa.get(
        categoria,
        categoria,
    )


def _gerar_template_camiseta(
    largura_relativa,
):
    """
    Gera uma estrutura visual simples
    para uma camiseta.

    A estrutura é apenas um template
    geométrico 2D da peça.

    Não representa molde industrial,
    costura real ou simulação de tecido.
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

    # ------------------------------------------------------
    # Referências verticais internas da peça.
    #
    # São posições visuais do template,
    # não medidas físicas adicionais.
    # ------------------------------------------------------

    y_topo = 0.0
    y_ombros = 0.08
    y_axilas = 0.24
    y_barra = 1.0

    # ------------------------------------------------------
    # Mangas
    #
    # São extensões gráficas proporcionais
    # ao próprio template.
    # ------------------------------------------------------

    extensao_manga = (
        largura_relativa
        * 0.18
    )

    queda_manga = 0.22

    # ------------------------------------------------------
    # Gola
    # ------------------------------------------------------

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
            "template_camiseta_2d"
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
                "tipo": (
                    "poligono"
                ),

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


def gerar_representacao_roupa_v1(
    produto: dict,
):
    """
    Gera a Representação da Roupa V1.

    Esta camada transforma os dados
    cadastrados da peça em uma descrição
    visual proporcional própria.

    IMPORTANTE:

    Esta função NÃO:
    - mede o corpo;
    - converte corpo para centímetros;
    - compara centímetros da peça
      com geometria corporal normalizada;
    - recomenda tamanho;
    - veste o avatar;
    - simula tecido;
    - simula caimento;
    - gera imagem final.

    As dimensões físicas cadastradas
    pertencem exclusivamente à peça.

    O sistema utiliza apenas a razão entre
    largura e comprimento da própria roupa
    para construir sua representação visual.
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

    categoria = (
        _normalizar_categoria(
            produto.get(
                "categoria"
            )
        )
    )

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
    # VALIDAÇÃO DIMENSIONAL DA PEÇA
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

            "pronta_para_vestir_avatar": False,

            "mensagem": (
                "A peça não possui largura e "
                "comprimento válidos para gerar "
                "uma representação visual proporcional."
            ),
        }

    # ======================================================
    # SISTEMA PROPORCIONAL DA ROUPA
    # ======================================================

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
    # TEMPLATE POR CATEGORIA
    # ======================================================

    template = None

    if categoria == "camiseta":
        template = (
            _gerar_template_camiseta(
                largura_relativa=(
                    largura_normalizada
                )
            )
        )

    # ======================================================
    # CATEGORIA AINDA NÃO IMPLEMENTADA
    # ======================================================

    if template is None:
        return {
            "versao": (
                "representacao_roupa_v1"
            ),

            "status": (
                "categoria_nao_implementada"
            ),

            "disponivel": False,

            "categoria": (
                categoria
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

                "modelagem": (
                    modelagem
                ),
            },

            "pronta_para_vestir_avatar": False,

            "mensagem": (
                "A categoria da peça ainda não possui "
                "template visual implementado."
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
            "a partir das dimensões cadastradas da peça. "
            "A geometria é proporcional à própria roupa "
            "e ainda não foi aplicada ao avatar."
        ),
    }