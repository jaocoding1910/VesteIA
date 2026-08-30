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


def _extrair_xy(
    ponto,
):
    """
    Extrai coordenadas x e y
    de um ponto.
    """

    if not isinstance(
        ponto,
        dict,
    ):
        return None

    x = _numero(
        ponto.get(
            "x"
        )
    )

    y = _numero(
        ponto.get(
            "y"
        )
    )

    if (
        x is None
        or y is None
    ):
        return None

    return (
        x,
        y,
    )


def _transformar_ponto_roupa(
    ponto,
    centro_roupa_x,
    centro_avatar_x,
    ombro_roupa_y,
    ombro_avatar_y,
    escala_visual,
):
    """
    Transforma um ponto do espaço local
    da roupa para o espaço do renderer
    do avatar.

    A transformação utiliza:
    - centralização horizontal;
    - alinhamento vertical dos ombros;
    - escala visual uniforme.

    Não utiliza centímetros corporais.
    """

    coordenadas = (
        _extrair_xy(
            ponto
        )
    )

    if coordenadas is None:
        return None

    x_local, y_local = (
        coordenadas
    )

    x_renderer = (
        centro_avatar_x
        + (
            x_local
            - centro_roupa_x
        )
        * escala_visual
    )

    y_renderer = (
        ombro_avatar_y
        + (
            y_local
            - ombro_roupa_y
        )
        * escala_visual
    )

    return {
        "x": (
            _arredondar(
                x_renderer
            )
        ),

        "y": (
            _arredondar(
                y_renderer
            )
        ),

        "origem": (
            "representacao_roupa_v1"
        ),
    }


def vestir_avatar_2d_v1(
    renderer_avatar_2d: dict,
    representacao_roupa: dict,
):
    """
    Posiciona uma representação visual
    de roupa sobre o Renderer do Avatar 2D.

    ETAPA 9 DO VESTEIA.

    Esta função executa somente
    posicionamento estrutural.

    A peça é ancorada visualmente
    na região dos ombros.

    IMPORTANTE:

    Esta função NÃO:
    - converte o corpo para centímetros;
    - compara cm da roupa com cm corporais;
    - recomenda tamanho;
    - calcula folga física;
    - interpreta modelagem;
    - interpreta preferência de caimento;
    - simula tecido;
    - simula deformação;
    - simula caimento;
    - altera anatomia;
    - gera imagem final.

    A Etapa 10 será responsável
    pela simulação visual de caimento.
    """

    # ======================================================
    # VALIDAÇÃO DO RENDERER
    # ======================================================

    if not isinstance(
        renderer_avatar_2d,
        dict,
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "renderer_invalido"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    if not renderer_avatar_2d.get(
        "pronto",
        False,
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "renderer_nao_pronto"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    # ======================================================
    # VALIDAÇÃO DA ROUPA
    # ======================================================

    if not isinstance(
        representacao_roupa,
        dict,
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "representacao_roupa_invalida"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    if not representacao_roupa.get(
        "pronta_para_vestir_avatar",
        False,
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "roupa_nao_pronta"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    # ======================================================
    # DADOS DO AVATAR
    # ======================================================

    pontos_avatar = (
        renderer_avatar_2d.get(
            "pontos"
        )
        or {}
    )

    ombro_avatar_a = (
        pontos_avatar.get(
            "ombro_esquerdo"
        )
        or {}
    )

    ombro_avatar_b = (
        pontos_avatar.get(
            "ombro_direito"
        )
        or {}
    )

    coordenadas_ombro_a = (
        _extrair_xy(
            ombro_avatar_a
        )
    )

    coordenadas_ombro_b = (
        _extrair_xy(
            ombro_avatar_b
        )
    )

    if (
        coordenadas_ombro_a is None
        or coordenadas_ombro_b is None
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "ombros_avatar_indisponiveis"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    (
        ombro_avatar_a_x,
        ombro_avatar_a_y,
    ) = coordenadas_ombro_a

    (
        ombro_avatar_b_x,
        ombro_avatar_b_y,
    ) = coordenadas_ombro_b

    largura_ombros_avatar = abs(
        ombro_avatar_a_x
        - ombro_avatar_b_x
    )

    centro_ombros_avatar_x = (
        (
            ombro_avatar_a_x
            + ombro_avatar_b_x
        )
        / 2
    )

    centro_ombros_avatar_y = (
        (
            ombro_avatar_a_y
            + ombro_avatar_b_y
        )
        / 2
    )

    # ======================================================
    # DADOS DA ROUPA
    # ======================================================

    template = (
        representacao_roupa.get(
            "template"
        )
        or {}
    )

    pontos_roupa = (
        template.get(
            "pontos"
        )
        or {}
    )

    ombro_roupa_a = (
        pontos_roupa.get(
            "ombro_esquerdo"
        )
        or {}
    )

    ombro_roupa_b = (
        pontos_roupa.get(
            "ombro_direito"
        )
        or {}
    )

    coordenadas_roupa_a = (
        _extrair_xy(
            ombro_roupa_a
        )
    )

    coordenadas_roupa_b = (
        _extrair_xy(
            ombro_roupa_b
        )
    )

    if (
        coordenadas_roupa_a is None
        or coordenadas_roupa_b is None
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "ombros_roupa_indisponiveis"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    (
        ombro_roupa_a_x,
        ombro_roupa_a_y,
    ) = coordenadas_roupa_a

    (
        ombro_roupa_b_x,
        ombro_roupa_b_y,
    ) = coordenadas_roupa_b

    largura_ombros_roupa = abs(
        ombro_roupa_a_x
        - ombro_roupa_b_x
    )

    centro_ombros_roupa_x = (
        (
            ombro_roupa_a_x
            + ombro_roupa_b_x
        )
        / 2
    )

    centro_ombros_roupa_y = (
        (
            ombro_roupa_a_y
            + ombro_roupa_b_y
        )
        / 2
    )

    # ======================================================
    # VALIDAÇÃO DAS LARGURAS
    # ======================================================

    if (
        largura_ombros_avatar <= 0
        or largura_ombros_roupa <= 0
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "largura_ombros_invalida"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    # ======================================================
    # ESCALA VISUAL DE ANCORAGEM
    #
    # Aqui NÃO existe comparação física.
    #
    # A largura estrutural dos ombros
    # do template é ajustada visualmente
    # à largura estrutural dos ombros
    # do avatar.
    #
    # Modelagem e folga NÃO entram aqui.
    # ======================================================

    escala_visual = (
        largura_ombros_avatar
        / largura_ombros_roupa
    )

    # ======================================================
    # TRANSFORMAÇÃO DOS PONTOS DA ROUPA
    # ======================================================

    pontos_roupa_no_avatar = {}

    for (
        nome,
        ponto,
    ) in pontos_roupa.items():

        pontos_roupa_no_avatar[
            nome
        ] = (
            _transformar_ponto_roupa(
                ponto=ponto,

                centro_roupa_x=(
                    centro_ombros_roupa_x
                ),

                centro_avatar_x=(
                    centro_ombros_avatar_x
                ),

                ombro_roupa_y=(
                    centro_ombros_roupa_y
                ),

                ombro_avatar_y=(
                    centro_ombros_avatar_y
                ),

                escala_visual=(
                    escala_visual
                ),
            )
        )

    # ======================================================
    # REGIÕES DA ROUPA
    # ======================================================

    regioes_origem = (
        template.get(
            "regioes"
        )
        or {}
    )

    regioes_avatar = {}

    for (
        nome_regiao,
        regiao,
    ) in regioes_origem.items():

        if not isinstance(
            regiao,
            dict,
        ):
            continue

        nomes_pontos = (
            regiao.get(
                "pontos"
            )
            or []
        )

        disponivel = all(
            pontos_roupa_no_avatar.get(
                nome
            )
            is not None
            for nome in nomes_pontos
        )

        regioes_avatar[
            nome_regiao
        ] = {
            "tipo": (
                regiao.get(
                    "tipo"
                )
            ),

            "pontos": (
                nomes_pontos
            ),

            "disponivel": (
                disponivel
            ),
        }

    # ======================================================
    # VALIDAÇÃO DO ALINHAMENTO DOS OMBROS
    # ======================================================

    ombros_roupa_transformados = [
        pontos_roupa_no_avatar.get(
            "ombro_esquerdo"
        ),

        pontos_roupa_no_avatar.get(
            "ombro_direito"
        ),
    ]

    ombros_roupa_transformados = [
        ponto
        for ponto in ombros_roupa_transformados
        if isinstance(
            ponto,
            dict,
        )
    ]

    largura_ombros_roupa_renderer = None

    if len(
        ombros_roupa_transformados
    ) == 2:

        largura_ombros_roupa_renderer = abs(
            ombros_roupa_transformados[
                0
            ][
                "x"
            ]
            - ombros_roupa_transformados[
                1
            ][
                "x"
            ]
        )

        largura_ombros_roupa_renderer = (
            _arredondar(
                largura_ombros_roupa_renderer
            )
        )

    diferenca_alinhamento = None

    if (
        largura_ombros_roupa_renderer
        is not None
    ):
        diferenca_alinhamento = abs(
            largura_ombros_avatar
            - largura_ombros_roupa_renderer
        )

        diferenca_alinhamento = (
            _arredondar(
                diferenca_alinhamento
            )
        )

    # ======================================================
    # QUALIDADE
    # ======================================================

    total_pontos = len(
        pontos_roupa_no_avatar
    )

    pontos_disponiveis = sum(
        ponto is not None
        for ponto in (
            pontos_roupa_no_avatar.values()
        )
    )

    percentual_pontos = (
        pontos_disponiveis
        / total_pontos
        if total_pontos
        else 0
    )

    tronco_disponivel = (
        regioes_avatar
        .get(
            "tronco",
            {},
        )
        .get(
            "disponivel",
            False,
        )
    )

    vestimenta_pronta = (
        tronco_disponivel
        and percentual_pontos >= 0.80
    )

    if vestimenta_pronta:
        status = (
            "roupa_posicionada_no_avatar"
        )

    elif pontos_disponiveis > 0:
        status = (
            "roupa_posicionada_parcialmente"
        )

    else:
        status = (
            "roupa_nao_posicionada"
        )

    # ======================================================
    # SAÍDA FINAL
    # ======================================================

    return {
        "versao": (
            "vestimenta_avatar_2d_v1"
        ),

        "status": (
            status
        ),

        "disponivel": (
            pontos_disponiveis > 0
        ),

        "origem": {
            "avatar": (
                "renderer_avatar_2d_v1"
            ),

            "roupa": (
                "representacao_roupa_v1"
            ),
        },

        "produto": (
            representacao_roupa.get(
                "produto"
            )
        ),

        "ancoragem": {
            "tipo": (
                "ombros_visual"
            ),

            "centro_avatar_x": (
                _arredondar(
                    centro_ombros_avatar_x
                )
            ),

            "centro_avatar_y": (
                _arredondar(
                    centro_ombros_avatar_y
                )
            ),

            "centro_roupa_local_x": (
                _arredondar(
                    centro_ombros_roupa_x
                )
            ),

            "centro_roupa_local_y": (
                _arredondar(
                    centro_ombros_roupa_y
                )
            ),

            "largura_ombros_avatar": (
                _arredondar(
                    largura_ombros_avatar
                )
            ),

            "largura_ombros_template": (
                _arredondar(
                    largura_ombros_roupa
                )
            ),

            "escala_visual": (
                _arredondar(
                    escala_visual
                )
            ),

            "escala_fisica": False,

            "usa_centimetros_corpo": False,
        },

        "pontos_roupa_no_avatar": (
            pontos_roupa_no_avatar
        ),

        "regioes": (
            regioes_avatar
        ),

        "validacao_alinhamento": {
            "largura_ombros_avatar": (
                _arredondar(
                    largura_ombros_avatar
                )
            ),

            "largura_ombros_roupa_renderer": (
                largura_ombros_roupa_renderer
            ),

            "diferenca": (
                diferenca_alinhamento
            ),

            "alinhamento_visual": (
                diferenca_alinhamento is not None
                and diferenca_alinhamento <= 0.001
            ),
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

            "tronco_disponivel": (
                tronco_disponivel
            ),
        },

        "capacidades": {
            "roupa_posicionada": (
                vestimenta_pronta
            ),

            "roupa_desenhavel": (
                vestimenta_pronta
            ),

            "simulacao_caimento_disponivel": (
                vestimenta_pronta
            ),

            "imagem_final_geravel": False,
        },

        "restricoes": {
            "usa_centimetros_corpo": False,

            "compara_cm_corpo_roupa": False,

            "recomenda_tamanho": False,

            "interpreta_modelagem": False,

            "aplica_preferencia_caimento": False,

            "simula_tecido": False,

            "simula_caimento": False,

            "deforma_corpo": False,
        },

        "vestida_no_avatar": (
            vestimenta_pronta
        ),

        "caimento_simulado": False,

        "pronta_para_simulacao_caimento": (
            vestimenta_pronta
        ),

        "imagem_gerada": False,

        "experimental": True,

        "mensagem": (
            "A roupa foi posicionada estruturalmente "
            "sobre o Avatar 2D utilizando os ombros "
            "como âncora visual. Nenhum caimento, "
            "folga física ou recomendação de tamanho "
            "foi calculado nesta etapa."
        ),
    }