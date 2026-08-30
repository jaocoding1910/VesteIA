def _arredondar(
    valor,
    casas=4,
):
    """
    Converte e arredonda um valor numérico
    de forma segura.
    """

    if valor is None:
        return None

    try:
        return round(
            float(valor),
            casas,
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def _dividir_seguro(
    numerador,
    denominador,
    casas=4,
):
    """
    Executa uma divisão somente quando
    os dois valores são válidos.

    Utilizado para transformar a geometria
    observada na fotografia em proporções
    internas independentes de centímetros.
    """

    numerador = _arredondar(
        numerador,
        casas=8,
    )

    denominador = _arredondar(
        denominador,
        casas=8,
    )

    if (
        numerador is None
        or denominador is None
        or denominador <= 0
    ):
        return None

    return round(
        numerador / denominador,
        casas,
    )


def gerar_estado_renderizacao_avatar_v1(
    avatar_corporal: dict,
):
    """
    Prepara o Estado de Renderização V1
    do Avatar VesteIA.

    Entrada:
    - avatar_corporal_v1

    Saída:
    - proporções normalizadas;
    - referência vertical do corpo;
    - parâmetros estruturais para
      futura camada de desenho/renderização.

    IMPORTANTE:

    Esta função NÃO:
    - executa MediaPipe;
    - acessa landmarks diretamente;
    - calcula centímetros;
    - estima altura física;
    - estima peso;
    - recomenda tamanho;
    - aplica roupa;
    - gera imagem;
    - altera o motor dimensional;
    - altera a Sprint 48.

    O sistema de referência utilizado aqui
    considera a altura visual do corpo como 1.0.
    """

    # ======================================================
    # VALIDAÇÃO DA ENTRADA
    # ======================================================

    if not isinstance(
        avatar_corporal,
        dict,
    ):
        return {
            "versao": (
                "estado_renderizacao_avatar_v1"
            ),

            "status": (
                "avatar_corporal_invalido"
            ),

            "disponivel": False,

            "origem": (
                "avatar_corporal_v1"
            ),

            "pronto_para_renderer": False,

            "renderizado": False,

            "experimental": True,

            "mensagem": (
                "O Avatar Corporal recebido "
                "é inválido."
            ),
        }

    avatar_disponivel = bool(
        avatar_corporal.get(
            "disponivel",
            False,
        )
    )

    if not avatar_disponivel:
        return {
            "versao": (
                "estado_renderizacao_avatar_v1"
            ),

            "status": (
                "avatar_corporal_indisponivel"
            ),

            "disponivel": False,

            "origem": (
                "avatar_corporal_v1"
            ),

            "pronto_para_renderer": False,

            "renderizado": False,

            "experimental": True,

            "mensagem": (
                "O Avatar Corporal não possui "
                "estrutura suficiente para "
                "preparar a renderização."
            ),
        }

    # ======================================================
    # FONTES
    # ======================================================

    estrutura = (
        avatar_corporal.get(
            "estrutura"
        )
        or {}
    )

    qualidade = (
        avatar_corporal.get(
            "qualidade_origem"
        )
        or {}
    )

    renderizacao_avatar = (
        avatar_corporal.get(
            "renderizacao"
        )
        or {}
    )

    # ======================================================
    # GEOMETRIA ORIGINAL DO AVATAR
    # ======================================================

    largura_ombros = _arredondar(
        estrutura.get(
            "largura_ombros_relativa"
        )
    )

    largura_torax = _arredondar(
        estrutura.get(
            "largura_torax_relativa"
        )
    )

    largura_quadril = _arredondar(
        estrutura.get(
            "largura_quadril_relativa"
        )
    )

    comprimento_tronco = _arredondar(
        estrutura.get(
            "comprimento_tronco_relativo"
        )
    )

    altura_corpo = _arredondar(
        estrutura.get(
            "altura_corpo_relativa"
        )
    )

    proporcao_ombros_quadril = (
        _arredondar(
            estrutura.get(
                "proporcao_ombros_quadril"
            )
        )
    )

    # ======================================================
    # NORMALIZAÇÃO PARA ESPAÇO DO AVATAR
    # ======================================================
    #
    # A altura visual do corpo passa a ser 1.0.
    #
    # Exemplo:
    #
    # largura_ombros_avatar =
    # largura_ombros_relativa
    # / altura_corpo_relativa
    #
    # Isso evita utilizar diretamente
    # o tamanho que o corpo ocupava
    # dentro da fotografia.
    # ======================================================

    ombros_por_altura = (
        _dividir_seguro(
            largura_ombros,
            altura_corpo,
        )
    )

    torax_por_altura = (
        _dividir_seguro(
            largura_torax,
            altura_corpo,
        )
    )

    quadril_por_altura = (
        _dividir_seguro(
            largura_quadril,
            altura_corpo,
        )
    )

    tronco_por_altura = (
        _dividir_seguro(
            comprimento_tronco,
            altura_corpo,
        )
    )

    # ======================================================
    # COMPLETUDE
    # ======================================================

    proporcoes_necessarias = (
        ombros_por_altura,
        torax_por_altura,
        quadril_por_altura,
        tronco_por_altura,
    )

    quantidade_proporcoes = sum(
        valor is not None
        for valor in proporcoes_necessarias
    )

    estrutura_normalizada_completa = (
        quantidade_proporcoes
        == len(
            proporcoes_necessarias
        )
    )

    # ======================================================
    # QUALIDADE DA ORIGEM
    # ======================================================

    geometria_consistente = bool(
        qualidade.get(
            "geometria_consistente",
            False,
        )
    )

    pose_apta = bool(
        qualidade.get(
            "pose_apta",
            False,
        )
    )

    qualidade_nivel = (
        qualidade.get(
            "nivel",
            "indisponivel",
        )
    )

    qualidade_pontuacao = (
        _arredondar(
            qualidade.get(
                "pontuacao"
            )
        )
    )

    avatar_pronto_renderizacao = bool(
        renderizacao_avatar.get(
            "pronto_para_renderizacao",
            False,
        )
    )

    # ======================================================
    # LIBERAÇÃO PARA RENDERER
    # ======================================================

    pronto_para_renderer = (
        avatar_pronto_renderizacao
        and estrutura_normalizada_completa
        and geometria_consistente
        and pose_apta
    )

    if pronto_para_renderer:
        status = (
            "estado_renderizacao_pronto"
        )

    elif quantidade_proporcoes > 0:
        status = (
            "estado_renderizacao_parcial"
        )

    else:
        status = (
            "estado_renderizacao_indisponivel"
        )

    # ======================================================
    # ESTADO DE RENDERIZAÇÃO
    # ======================================================

    return {
        "versao": (
            "estado_renderizacao_avatar_v1"
        ),

        "status": (
            status
        ),

        "disponivel": (
            quantidade_proporcoes > 0
        ),

        "origem": (
            "avatar_corporal_v1"
        ),

        "sistema_referencia": {
            "tipo": (
                "corpo_normalizado"
            ),

            "altura_corpo": 1.0,

            "unidade": (
                "proporcao_da_altura_visual"
            ),

            "origem_metrica_cm": False,

            "escala_fisica": False,

            "independente_de_altura_real": True,

            "descricao": (
                "A altura visual observada "
                "do corpo é utilizada como "
                "referência proporcional 1.0."
            ),
        },

        "proporcoes_renderizacao": {
            "largura_ombros": (
                ombros_por_altura
            ),

            "largura_torax": (
                torax_por_altura
            ),

            "largura_quadril": (
                quadril_por_altura
            ),

            "comprimento_tronco": (
                tronco_por_altura
            ),

            "altura_corpo": 1.0,

            "proporcao_ombros_quadril": (
                proporcao_ombros_quadril
            ),

            "completa": (
                estrutura_normalizada_completa
            ),
        },

        "eixo_corporal": {
            "centro_horizontal": 0.5,

            "referencia_vertical_superior": 0.0,

            "referencia_vertical_inferior": 1.0,

            "altura_normalizada": 1.0,

            "tipo": (
                "eixo_central_normalizado"
            ),
        },

        "regioes_renderizaveis": {
            "ombros": (
                ombros_por_altura
                is not None
            ),

            "torax": (
                torax_por_altura
                is not None
            ),

            "quadril": (
                quadril_por_altura
                is not None
            ),

            "tronco": (
                tronco_por_altura
                is not None
            ),
        },

        "qualidade_origem": {
            "nivel": (
                qualidade_nivel
            ),

            "pontuacao": (
                qualidade_pontuacao
            ),

            "geometria_consistente": (
                geometria_consistente
            ),

            "pose_apta": (
                pose_apta
            ),
        },

        "renderer": {
            "pronto": (
                pronto_para_renderer
            ),

            "motor": None,

            "tipo_previsto": (
                "renderer_avatar_proporcional"
            ),

            "imagem_gerada": False,

            "malha_2d_gerada": False,

            "malha_3d_gerada": False,

            "textura_corporal_gerada": False,
        },

        "produto_virtual": {
            "produto_aplicado": False,

            "roupa_renderizada": False,

            "deformacao_roupa_aplicada": False,

            "simulacao_caimento_aplicada": False,
        },

        "restricoes": {
            "usa_centimetros": False,

            "estima_altura_fisica": False,

            "estima_peso": False,

            "estima_circunferencias": False,

            "recomenda_tamanho": False,

            "representa_medida_antropometrica": False,
        },

        "pronto_para_renderer": (
            pronto_para_renderer
        ),

        "renderizado": False,

        "experimental": True,

        "mensagem": (
            "Estado de renderização do Avatar "
            "preparado em espaço corporal "
            "normalizado. As proporções são "
            "visuais e não representam medidas "
            "antropométricas em centímetros."
        ),
    }