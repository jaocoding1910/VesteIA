from math import sqrt

from app.services.categorias_vestuario import (
    normalizar_categoria,
    obter_familia_categoria,
)


def _numero(valor):
    """
    Converte valor para float
    de forma segura.
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
    Arredonda valor numérico
    de forma segura.
    """

    valor = _numero(valor)

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
    Verifica se um ponto contém
    coordenadas numéricas válidas.
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

    return (
        x is not None
        and y is not None
    )


def _centro_entre_pontos(
    ponto_a,
    ponto_b,
):
    """
    Retorna o centro visual
    entre dois pontos.
    """

    if (
        not _ponto_valido(ponto_a)
        or not _ponto_valido(ponto_b)
    ):
        return None

    return {
        "x": (
            (
                ponto_a["x"]
                + ponto_b["x"]
            )
            / 2
        ),

        "y": (
            (
                ponto_a["y"]
                + ponto_b["y"]
            )
            / 2
        ),
    }


def _largura_horizontal(
    ponto_a,
    ponto_b,
):
    """
    Calcula somente a distância horizontal
    entre dois pontos do renderer.

    A unidade continua sendo visual/normalizada.
    """

    if (
        not _ponto_valido(ponto_a)
        or not _ponto_valido(ponto_b)
    ):
        return None

    return abs(
        ponto_b["x"]
        - ponto_a["x"]
    )


def _interpolar(
    inicio,
    fim,
    fator,
):
    """
    Interpolação visual simples
    entre duas coordenadas.
    """

    inicio = _numero(inicio)
    fim = _numero(fim)
    fator = _numero(fator)

    if (
        inicio is None
        or fim is None
        or fator is None
    ):
        return None

    return (
        inicio
        + (
            fim
            - inicio
        )
        * fator
    )


def _transformar_ponto(
    ponto,
    centro_local_x,
    centro_local_y,
    centro_avatar_x,
    centro_avatar_y,
    escala_x,
    escala_y,
):
    """
    Transforma um ponto da roupa
    do sistema local do template
    para o sistema do Avatar 2D.

    A transformação é exclusivamente
    visual e proporcional.
    """

    if not _ponto_valido(
        ponto
    ):
        return None

    x = _numero(
        ponto.get("x")
    )

    y = _numero(
        ponto.get("y")
    )

    novo_x = (
        centro_avatar_x
        + (
            x
            - centro_local_x
        )
        * escala_x
    )

    novo_y = (
        centro_avatar_y
        + (
            y
            - centro_local_y
        )
        * escala_y
    )

    return {
        "x": (
            _arredondar(
                novo_x
            )
        ),

        "y": (
            _arredondar(
                novo_y
            )
        ),

        "origem": (
            "representacao_roupa_v1"
        ),
    }


def _transformar_regioes(
    regioes_origem,
    pontos_transformados,
):
    """
    Reconstrói as regiões da roupa
    após posicionamento no avatar.
    """

    resultado = {}

    if not isinstance(
        regioes_origem,
        dict,
    ):
        return resultado

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
            regiao.get("pontos")
            or []
        )

        disponivel = all(
            pontos_transformados.get(
                nome
            )
            is not None
            for nome in nomes_pontos
        )

        resultado[
            nome_regiao
        ] = {
            "tipo": (
                regiao.get("tipo")
            ),

            "pontos": (
                nomes_pontos
            ),

            "disponivel": (
                disponivel
            ),
        }

    return resultado


# ==========================================================
# ALVOS VERTICAIS
# ==========================================================

def _obter_y_medio(
    pontos_avatar,
    nome_a,
    nome_b,
):
    """
    Retorna a média vertical de
    dois landmarks do Avatar.
    """

    ponto_a = (
        pontos_avatar.get(
            nome_a
        )
    )

    ponto_b = (
        pontos_avatar.get(
            nome_b
        )
    )

    centro = (
        _centro_entre_pontos(
            ponto_a,
            ponto_b,
        )
    )

    if centro is None:
        return None

    return centro["y"]


def _obter_alvo_vertical_inferior(
    categoria,
    pontos_avatar,
    centro_quadril_y,
):
    """
    Define até onde a peça inferior
    deve se estender visualmente.

    Não representa comprimento físico.
    """

    y_joelhos = (
        _obter_y_medio(
            pontos_avatar,
            "joelho_esquerdo",
            "joelho_direito",
        )
    )

    y_tornozelos = (
        _obter_y_medio(
            pontos_avatar,
            "tornozelo_esquerdo",
            "tornozelo_direito",
        )
    )

    if categoria == "short":
        if y_joelhos is not None:
            return _interpolar(
                centro_quadril_y,
                y_joelhos,
                0.58,
            )

    elif categoria == "bermuda":
        if y_joelhos is not None:
            return _interpolar(
                centro_quadril_y,
                y_joelhos,
                0.92,
            )

    elif categoria == "saia":
        if (
            y_joelhos is not None
            and y_tornozelos is not None
        ):
            return _interpolar(
                y_joelhos,
                y_tornozelos,
                0.18,
            )

        if y_joelhos is not None:
            return y_joelhos

    else:
        # Calça e demais inferiores longos.
        if y_tornozelos is not None:
            return y_tornozelos

    return None


def _obter_alvo_vertical_integrado(
    categoria,
    pontos_avatar,
    centro_ombros_y,
):
    """
    Define o limite vertical visual
    para vestido e macacão.
    """

    y_joelhos = (
        _obter_y_medio(
            pontos_avatar,
            "joelho_esquerdo",
            "joelho_direito",
        )
    )

    y_tornozelos = (
        _obter_y_medio(
            pontos_avatar,
            "tornozelo_esquerdo",
            "tornozelo_direito",
        )
    )

    if categoria == "macacao":
        if y_tornozelos is not None:
            return y_tornozelos

    if categoria == "vestido":
        if (
            y_joelhos is not None
            and y_tornozelos is not None
        ):
            return _interpolar(
                y_joelhos,
                y_tornozelos,
                0.38,
            )

        if y_joelhos is not None:
            return y_joelhos

    return None


# ==========================================================
# CALÇADOS
# ==========================================================

def _gerar_poligono_pe(
    calcanhar,
    ponta,
    prefixo,
):
    """
    Constrói um pequeno polígono visual
    ao redor do segmento real do pé.

    Os pontos adicionais são somente
    acabamento gráfico do renderer.
    """

    if (
        not _ponto_valido(calcanhar)
        or not _ponto_valido(ponta)
    ):
        return None

    dx = (
        ponta["x"]
        - calcanhar["x"]
    )

    dy = (
        ponta["y"]
        - calcanhar["y"]
    )

    comprimento = sqrt(
        dx * dx
        + dy * dy
    )

    if comprimento <= 0:
        return None

    normal_x = (
        -dy
        / comprimento
    )

    normal_y = (
        dx
        / comprimento
    )

    largura_calcanhar = (
        comprimento
        * 0.20
    )

    largura_ponta = (
        comprimento
        * 0.25
    )

    pontos = {
        f"{prefixo}_calcanhar_externo": {
            "x": _arredondar(
                calcanhar["x"]
                + normal_x
                * largura_calcanhar
            ),
            "y": _arredondar(
                calcanhar["y"]
                + normal_y
                * largura_calcanhar
            ),
            "origem": (
                "renderer_avatar_2d_v1"
            ),
        },

        f"{prefixo}_calcanhar_interno": {
            "x": _arredondar(
                calcanhar["x"]
                - normal_x
                * largura_calcanhar
            ),
            "y": _arredondar(
                calcanhar["y"]
                - normal_y
                * largura_calcanhar
            ),
            "origem": (
                "renderer_avatar_2d_v1"
            ),
        },

        f"{prefixo}_ponta_interna": {
            "x": _arredondar(
                ponta["x"]
                - normal_x
                * largura_ponta
            ),
            "y": _arredondar(
                ponta["y"]
                - normal_y
                * largura_ponta
            ),
            "origem": (
                "renderer_avatar_2d_v1"
            ),
        },

        f"{prefixo}_ponta_externa": {
            "x": _arredondar(
                ponta["x"]
                + normal_x
                * largura_ponta
            ),
            "y": _arredondar(
                ponta["y"]
                + normal_y
                * largura_ponta
            ),
            "origem": (
                "renderer_avatar_2d_v1"
            ),
        },
    }

    return pontos


def _vestir_calcado(
    renderer_avatar_2d,
    representacao_roupa,
    categoria,
    familia,
):
    """
    Posiciona uma representação visual
    em cada pé detectado.

    Não calcula número de calçado nem
    comprimento físico do pé.
    """

    pontos_avatar = (
        renderer_avatar_2d.get(
            "pontos"
        )
        or {}
    )

    calcanhar_esquerdo = (
        pontos_avatar.get(
            "calcanhar_esquerdo"
        )
    )

    ponta_esquerda = (
        pontos_avatar.get(
            "ponta_pe_esquerdo"
        )
    )

    calcanhar_direito = (
        pontos_avatar.get(
            "calcanhar_direito"
        )
    )

    ponta_direita = (
        pontos_avatar.get(
            "ponta_pe_direito"
        )
    )

    pontos_esquerdo = (
        _gerar_poligono_pe(
            calcanhar_esquerdo,
            ponta_esquerda,
            "pe_esquerdo",
        )
    )

    pontos_direito = (
        _gerar_poligono_pe(
            calcanhar_direito,
            ponta_direita,
            "pe_direito",
        )
    )

    if (
        pontos_esquerdo is None
        or pontos_direito is None
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "ancoragem_calcado_indisponivel"
            ),

            "disponivel": False,

            "categoria": categoria,

            "familia": familia,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    pontos_roupa = {
        **pontos_esquerdo,
        **pontos_direito,
    }

    regioes = {
        "pe_esquerdo": {
            "tipo": (
                "poligono"
            ),

            "pontos": [
                "pe_esquerdo_calcanhar_externo",
                "pe_esquerdo_ponta_externa",
                "pe_esquerdo_ponta_interna",
                "pe_esquerdo_calcanhar_interno",
            ],

            "disponivel": True,
        },

        "pe_direito": {
            "tipo": (
                "poligono"
            ),

            "pontos": [
                "pe_direito_calcanhar_externo",
                "pe_direito_ponta_externa",
                "pe_direito_ponta_interna",
                "pe_direito_calcanhar_interno",
            ],

            "disponivel": True,
        },
    }

    produto = (
        representacao_roupa.get(
            "produto"
        )
        or {}
    )

    return {
        "versao": (
            "vestimenta_avatar_2d_v1"
        ),

        "status": (
            "roupa_posicionada_no_avatar"
        ),

        "disponivel": True,

        "categoria": categoria,

        "familia": familia,

        "origem": {
            "avatar": (
                "renderer_avatar_2d_v1"
            ),

            "roupa": (
                "representacao_roupa_v1"
            ),
        },

        "produto": (
            produto
        ),

        "ancoragem": {
            "tipo": (
                "pes_visuais"
            ),

            "ponto_a": (
                "calcanhar"
            ),

            "ponto_b": (
                "ponta_pe"
            ),

            "escala_fisica": False,

            "usa_centimetros_corpo": False,
        },

        "pontos_roupa_no_avatar": (
            pontos_roupa
        ),

        "regioes": (
            regioes
        ),

        "validacao_alinhamento": {
            "tipo_ancoragem": (
                "pes_visuais"
            ),

            "alinhamento_visual": True,
        },

        "qualidade": {
            "pontos_disponiveis": (
                len(pontos_roupa)
            ),

            "total_pontos": 8,

            "percentual_pontos": 1.0,

            "regiao_principal": (
                "pes"
            ),

            "regiao_principal_disponivel": True,
        },

        "capacidades": {
            "roupa_posicionada": True,

            "roupa_desenhavel": True,

            "multivestimenta": True,

            "simulacao_caimento_disponivel": True,

            "imagem_final_geravel": False,
        },

        "restricoes": {
            "usa_centimetros_corpo": False,

            "compara_cm_corpo_roupa": False,

            "recomenda_tamanho": False,

            "interpreta_numero_calcado": False,

            "simula_tecido": False,

            "deforma_corpo": False,
        },

        "vestida_no_avatar": True,

        "caimento_simulado": False,

        "pronta_para_simulacao_caimento": True,

        "imagem_gerada": False,

        "experimental": True,

        "mensagem": (
            "O calçado foi posicionado visualmente "
            "sobre os segmentos reais dos pés "
            "detectados na fotografia."
        ),
    }


# ==========================================================
# FUNÇÃO PRINCIPAL
# ==========================================================

def vestir_avatar_2d_v1(
    renderer_avatar_2d: dict,
    representacao_roupa: dict,
):
    """
    Posiciona a Representação da Roupa V1
    sobre o Avatar Renderer 2D.

    Sprint Multivestimenta.

    Famílias suportadas:
    - superior;
    - inferior;
    - corpo_integrado;
    - calcado.

    IMPORTANTE:

    Esta etapa NÃO:
    - mede o corpo;
    - utiliza centímetros corporais;
    - compara cm do corpo com cm da peça;
    - recomenda tamanho;
    - simula tecido;
    - calcula folga física;
    - altera a anatomia detectada.

    O posicionamento é exclusivamente visual.
    """

    # ======================================================
    # VALIDAÇÕES
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
                "representacao_roupa_nao_pronta"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    # ======================================================
    # CATEGORIA / FAMÍLIA
    # ======================================================

    produto = (
        representacao_roupa.get(
            "produto"
        )
        or {}
    )

    categoria = (
        normalizar_categoria(
            representacao_roupa.get(
                "categoria"
            )
            or produto.get(
                "categoria"
            )
        )
    )

    familia = (
        representacao_roupa.get(
            "familia"
        )
        or produto.get(
            "familia"
        )
    )

    if (
        familia is None
        and categoria is not None
    ):
        familia = (
            obter_familia_categoria(
                categoria
            )
        )

    if (
        categoria is None
        or familia is None
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "categoria_ou_familia_indisponivel"
            ),

            "disponivel": False,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    # ======================================================
    # CALÇADO
    # ======================================================

    if familia == "calcado":
        return _vestir_calcado(
            renderer_avatar_2d=(
                renderer_avatar_2d
            ),

            representacao_roupa=(
                representacao_roupa
            ),

            categoria=(
                categoria
            ),

            familia=(
                familia
            ),
        )

    # ======================================================
    # PONTOS
    # ======================================================

    pontos_avatar = (
        renderer_avatar_2d.get(
            "pontos"
        )
        or {}
    )

    template = (
        representacao_roupa.get(
            "template"
        )
        or {}
    )

    pontos_template = (
        template.get(
            "pontos"
        )
        or {}
    )

    regioes_template = (
        template.get(
            "regioes"
        )
        or {}
    )

    referencias_template = (
        template.get(
            "referencias"
        )
        or {}
    )

    # ======================================================
    # ANCORAGEM POR FAMÍLIA
    # ======================================================

    ponto_avatar_a = None
    ponto_avatar_b = None

    ponto_template_a = None
    ponto_template_b = None

    tipo_ancoragem = None

    if familia in {
        "superior",
        "corpo_integrado",
    }:
        ponto_avatar_a = (
            pontos_avatar.get(
                "ombro_esquerdo"
            )
        )

        ponto_avatar_b = (
            pontos_avatar.get(
                "ombro_direito"
            )
        )

        ponto_template_a = (
            pontos_template.get(
                "ombro_esquerdo"
            )
        )

        ponto_template_b = (
            pontos_template.get(
                "ombro_direito"
            )
        )

        tipo_ancoragem = (
            "ombros_visuais"
        )

    elif familia == "inferior":
        ponto_avatar_a = (
            pontos_avatar.get(
                "quadril_esquerdo"
            )
        )

        ponto_avatar_b = (
            pontos_avatar.get(
                "quadril_direito"
            )
        )

        ponto_template_a = (
            pontos_template.get(
                "quadril_esquerdo"
            )
        )

        ponto_template_b = (
            pontos_template.get(
                "quadril_direito"
            )
        )

        tipo_ancoragem = (
            "quadril_visual"
        )

    else:
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "familia_nao_suportada"
            ),

            "disponivel": False,

            "categoria": categoria,

            "familia": familia,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    if (
        not _ponto_valido(
            ponto_avatar_a
        )
        or not _ponto_valido(
            ponto_avatar_b
        )
        or not _ponto_valido(
            ponto_template_a
        )
        or not _ponto_valido(
            ponto_template_b
        )
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "ancoragem_indisponivel"
            ),

            "disponivel": False,

            "categoria": categoria,

            "familia": familia,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    centro_avatar = (
        _centro_entre_pontos(
            ponto_avatar_a,
            ponto_avatar_b,
        )
    )

    centro_template = (
        _centro_entre_pontos(
            ponto_template_a,
            ponto_template_b,
        )
    )

    largura_avatar = (
        _largura_horizontal(
            ponto_avatar_a,
            ponto_avatar_b,
        )
    )

    largura_template = (
        _largura_horizontal(
            ponto_template_a,
            ponto_template_b,
        )
    )

    if (
        centro_avatar is None
        or centro_template is None
        or largura_avatar is None
        or largura_template is None
        or largura_template <= 0
    ):
        return {
            "versao": (
                "vestimenta_avatar_2d_v1"
            ),

            "status": (
                "escala_visual_indisponivel"
            ),

            "disponivel": False,

            "categoria": categoria,

            "familia": familia,

            "vestida_no_avatar": False,

            "pronta_para_simulacao_caimento": False,
        }

    escala_x = (
        largura_avatar
        / largura_template
    )

    # ======================================================
    # ESCALA VERTICAL
    #
    # Superior:
    # preserva inicialmente a proporção local.
    #
    # Inferior/integrado:
    # utiliza landmarks verticais reais do Avatar
    # como destino visual.
    # ======================================================

    escala_y = (
        escala_x
    )

    alvo_vertical = None

    if familia == "inferior":

        alvo_vertical = (
            _obter_alvo_vertical_inferior(
                categoria=(
                    categoria
                ),

                pontos_avatar=(
                    pontos_avatar
                ),

                centro_quadril_y=(
                    centro_avatar["y"]
                ),
            )
        )

        barra_local_y = (
            _numero(
                referencias_template.get(
                    "barra_y"
                )
            )
        )

        if (
            alvo_vertical is not None
            and barra_local_y is not None
            and barra_local_y
            != centro_template["y"]
        ):
            escala_y = (
                (
                    alvo_vertical
                    - centro_avatar["y"]
                )
                /
                (
                    barra_local_y
                    - centro_template["y"]
                )
            )

    elif familia == "corpo_integrado":

        alvo_vertical = (
            _obter_alvo_vertical_integrado(
                categoria=(
                    categoria
                ),

                pontos_avatar=(
                    pontos_avatar
                ),

                centro_ombros_y=(
                    centro_avatar["y"]
                ),
            )
        )

        barra_local_y = (
            _numero(
                referencias_template.get(
                    "barra_y"
                )
            )
        )

        if (
            alvo_vertical is not None
            and barra_local_y is not None
            and barra_local_y
            != centro_template["y"]
        ):
            escala_y = (
                (
                    alvo_vertical
                    - centro_avatar["y"]
                )
                /
                (
                    barra_local_y
                    - centro_template["y"]
                )
            )

    # Proteção contra escala invertida.
    if (
        escala_y is None
        or escala_y <= 0
    ):
        escala_y = escala_x

    # ======================================================
    # TRANSFORMAÇÃO
    # ======================================================

    pontos_roupa_no_avatar = {}

    for (
        nome,
        ponto,
    ) in pontos_template.items():

        pontos_roupa_no_avatar[
            nome
        ] = (
            _transformar_ponto(
                ponto=(
                    ponto
                ),

                centro_local_x=(
                    centro_template["x"]
                ),

                centro_local_y=(
                    centro_template["y"]
                ),

                centro_avatar_x=(
                    centro_avatar["x"]
                ),

                centro_avatar_y=(
                    centro_avatar["y"]
                ),

                escala_x=(
                    escala_x
                ),

                escala_y=(
                    escala_y
                ),
            )
        )

    regioes = (
        _transformar_regioes(
            regioes_origem=(
                regioes_template
            ),

            pontos_transformados=(
                pontos_roupa_no_avatar
            ),
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
            pontos_roupa_no_avatar
            .values()
        )
    )

    percentual_pontos = (
        pontos_disponiveis
        / total_pontos
        if total_pontos
        else 0
    )

    regioes_disponiveis = sum(
        regiao.get(
            "disponivel",
            False,
        )
        for regiao in (
            regioes.values()
        )
    )

    total_regioes = len(
        regioes
    )

    roupa_pronta = (
        total_pontos > 0
        and percentual_pontos >= 0.80
        and regioes_disponiveis > 0
    )

    # ======================================================
    # VALIDAÇÃO DA ÂNCORA
    # ======================================================

    largura_transformada = (
        largura_template
        * escala_x
    )

    diferenca_ancora = abs(
        largura_transformada
        - largura_avatar
    )

    alinhamento_visual = (
        diferenca_ancora
        <= 0.001
    )

    # ======================================================
    # SAÍDA
    # ======================================================

    return {
        "versao": (
            "vestimenta_avatar_2d_v1"
        ),

        "status": (
            "roupa_posicionada_no_avatar"
            if roupa_pronta
            else "roupa_posicionada_parcialmente"
        ),

        "disponivel": (
            roupa_pronta
        ),

        "categoria": (
            categoria
        ),

        "familia": (
            familia
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
            produto
        ),

        "ancoragem": {
            "tipo": (
                tipo_ancoragem
            ),

            "centro_avatar_x": (
                _arredondar(
                    centro_avatar["x"]
                )
            ),

            "centro_avatar_y": (
                _arredondar(
                    centro_avatar["y"]
                )
            ),

            "centro_roupa_local_x": (
                _arredondar(
                    centro_template["x"]
                )
            ),

            "centro_roupa_local_y": (
                _arredondar(
                    centro_template["y"]
                )
            ),

            "largura_ancora_avatar": (
                _arredondar(
                    largura_avatar
                )
            ),

            "largura_ancora_template": (
                _arredondar(
                    largura_template
                )
            ),

            # Compatibilidade com consumidores V1.
            "escala_visual": (
                _arredondar(
                    escala_x
                )
            ),

            "escala_visual_x": (
                _arredondar(
                    escala_x
                )
            ),

            "escala_visual_y": (
                _arredondar(
                    escala_y
                )
            ),

            "alvo_vertical_avatar_y": (
                _arredondar(
                    alvo_vertical
                )
            ),

            "escala_fisica": False,

            "usa_centimetros_corpo": False,
        },

        "pontos_roupa_no_avatar": (
            pontos_roupa_no_avatar
        ),

        "regioes": (
            regioes
        ),

        "validacao_alinhamento": {
            "tipo_ancoragem": (
                tipo_ancoragem
            ),

            "largura_ancora_avatar": (
                _arredondar(
                    largura_avatar
                )
            ),

            "largura_ancora_roupa_renderer": (
                _arredondar(
                    largura_transformada
                )
            ),

            "diferenca": (
                _arredondar(
                    diferenca_ancora
                )
            ),

            "alinhamento_visual": (
                alinhamento_visual
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

            "regioes_disponiveis": (
                regioes_disponiveis
            ),

            "total_regioes": (
                total_regioes
            ),

            "estrutura_familia_disponivel": (
                roupa_pronta
            ),
        },

        "capacidades": {
            "roupa_posicionada": (
                roupa_pronta
            ),

            "roupa_desenhavel": (
                roupa_pronta
            ),

            "multivestimenta": True,

            "simulacao_caimento_disponivel": (
                roupa_pronta
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
            roupa_pronta
        ),

        "caimento_simulado": False,

        "pronta_para_simulacao_caimento": (
            roupa_pronta
        ),

        "imagem_gerada": False,

        "experimental": True,

        "mensagem": (
            "A roupa foi posicionada sobre o Avatar 2D "
            "pela arquitetura multivestimenta do VesteIA. "
            "A família da peça define a âncora corporal "
            "e o posicionamento permanece exclusivamente visual."
        ),
    }