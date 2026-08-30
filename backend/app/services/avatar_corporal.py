def _arredondar(
    valor,
    casas=4,
):
    """
    Arredonda valores numéricos
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


def _classificar_relacao_horizontal(
    valor,
):
    """
    Classifica uma largura corporal relativa
    sem transformá-la em centímetros.

    A classificação é apenas estrutural
    dentro da própria representação visual.
    """

    valor = _arredondar(
        valor
    )

    if valor is None:
        return "indisponivel"

    if valor < 0.07:
        return "estreita"

    if valor < 0.10:
        return "moderada"

    return "ampla"


def _classificar_proporcao_tronco(
    proporcao,
):
    """
    Traduz a relação ombros/quadril
    para uma característica visual
    utilizável pelo Avatar VesteIA.
    """

    proporcao = _arredondar(
        proporcao
    )

    if proporcao is None:
        return "indisponivel"

    if proporcao >= 1.15:
        return "ombros_predominantes"

    if proporcao <= 0.85:
        return "quadril_predominante"

    return "equilibrado"


def gerar_avatar_corporal_v1(
    representacao_corporal: dict,
):
    """
    Constrói o Avatar Corporal V1
    a partir da representação corporal
    oficial do VesteIA.

    IMPORTANTE:

    Esta função NÃO:
    - lê landmarks diretamente;
    - executa MediaPipe;
    - estima altura física;
    - inventa centímetros;
    - recomenda tamanho;
    - altera o Sprint 48;
    - altera o ranking;
    - gera imagem realista.

    Ela cria uma descrição estrutural
    proporcional que poderá ser utilizada
    posteriormente por uma camada
    de renderização.
    """

    # ======================================================
    # VALIDAÇÃO DA ENTRADA
    # ======================================================

    if not isinstance(
        representacao_corporal,
        dict,
    ):
        return {
            "versao": "avatar_corporal_v1",
            "status": "representacao_corporal_invalida",
            "disponivel": False,
            "origem": "representacao_corporal_v1",
            "pronto_para_renderizacao": False,
            "gerado": False,
            "experimental": True,
            "mensagem": (
                "A representação corporal "
                "recebida é inválida."
            ),
        }

    representacao_disponivel = bool(
        representacao_corporal.get(
            "disponivel",
            False,
        )
    )

    if not representacao_disponivel:
        return {
            "versao": "avatar_corporal_v1",
            "status": "representacao_corporal_indisponivel",
            "disponivel": False,
            "origem": "representacao_corporal_v1",
            "pronto_para_renderizacao": False,
            "gerado": False,
            "experimental": True,
            "mensagem": (
                "A representação corporal "
                "não possui geometria suficiente "
                "para preparar o Avatar VesteIA."
            ),
        }

    # ======================================================
    # FONTES
    # ======================================================

    geometria = (
        representacao_corporal.get(
            "geometria_visual"
        )
        or {}
    )

    proporcoes = (
        representacao_corporal.get(
            "proporcoes"
        )
        or {}
    )

    qualidade = (
        representacao_corporal.get(
            "qualidade_visual"
        )
        or {}
    )

    escala_fisica = (
        representacao_corporal.get(
            "escala_fisica"
        )
        or {}
    )

    avatar_origem = (
        representacao_corporal.get(
            "avatar"
        )
        or {}
    )

    # ======================================================
    # GEOMETRIA
    # ======================================================

    largura_ombros = _arredondar(
        geometria.get(
            "largura_ombros_relativa"
        )
    )

    largura_quadril = _arredondar(
        geometria.get(
            "largura_quadril_relativa"
        )
    )

    largura_torax = _arredondar(
        geometria.get(
            "largura_torax_relativa"
        )
    )

    comprimento_tronco = _arredondar(
        geometria.get(
            "comprimento_tronco_relativo"
        )
    )

    altura_corpo = _arredondar(
        geometria.get(
            "altura_corpo_relativa"
        )
    )

    proporcao_ombros_quadril = (
        _arredondar(
            proporcoes.get(
                "ombros_quadril"
            )
        )
    )

    relacao_ombros_quadril = (
        proporcoes.get(
            "relacao_ombros_quadril"
        )
    )

    # ======================================================
    # COMPLETUDE
    # ======================================================

    valores_estruturais = (
        largura_ombros,
        largura_quadril,
        largura_torax,
        comprimento_tronco,
        altura_corpo,
    )

    quantidade_disponivel = sum(
        valor is not None
        for valor in valores_estruturais
    )

    estrutura_completa = (
        quantidade_disponivel
        == len(
            valores_estruturais
        )
    )

    # ======================================================
    # QUALIDADE
    # ======================================================

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

    # ======================================================
    # PERFIL PROPORCIONAL
    # ======================================================

    perfil_proporcional = {
        "ombros": (
            _classificar_relacao_horizontal(
                largura_ombros
            )
        ),

        "torax": (
            _classificar_relacao_horizontal(
                largura_torax
            )
        ),

        "quadril": (
            _classificar_relacao_horizontal(
                largura_quadril
            )
        ),

        "estrutura_tronco": (
            _classificar_proporcao_tronco(
                proporcao_ombros_quadril
            )
        ),

        "relacao_ombros_quadril": (
            relacao_ombros_quadril
        ),
    }

    # ======================================================
    # ESCALA
    # ======================================================

    escala_disponivel = bool(
        escala_fisica.get(
            "disponivel",
            False,
        )
    )

    # ======================================================
    # RENDERIZAÇÃO
    # ======================================================

    origem_apta_avatar = bool(
        avatar_origem.get(
            "pronta_para_avatar",
            False,
        )
    )

    pronto_para_renderizacao = (
        origem_apta_avatar
        and estrutura_completa
        and geometria_consistente
        and pose_apta
    )

    # ======================================================
    # STATUS
    # ======================================================

    if pronto_para_renderizacao:
        status = (
            "avatar_corporal_pronto"
        )

    elif quantidade_disponivel > 0:
        status = (
            "avatar_corporal_parcial"
        )

    else:
        status = (
            "avatar_corporal_indisponivel"
        )

    # ======================================================
    # CONTRATO DO AVATAR
    # ======================================================

    return {
        "versao": (
            "avatar_corporal_v1"
        ),

        "status": status,

        "disponivel": (
            quantidade_disponivel > 0
        ),

        "origem": (
            "representacao_corporal_v1"
        ),

        "estrutura": {
            "largura_ombros_relativa": (
                largura_ombros
            ),

            "largura_torax_relativa": (
                largura_torax
            ),

            "largura_quadril_relativa": (
                largura_quadril
            ),

            "comprimento_tronco_relativo": (
                comprimento_tronco
            ),

            "altura_corpo_relativa": (
                altura_corpo
            ),

            "proporcao_ombros_quadril": (
                proporcao_ombros_quadril
            ),

            "unidade": (
                "geometria_relativa_vesteia"
            ),

            "completa": (
                estrutura_completa
            ),
        },

        "perfil_proporcional": (
            perfil_proporcional
        ),

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

        "escala_fisica": {
            "disponivel": (
                escala_disponivel
            ),

            "necessaria_para_avatar_visual": False,

            "necessaria_para_renderizacao_proporcional": False,

            "altura_fisica_inferida": False,
        },

        "renderizacao": {
            "pronto_para_renderizacao": (
                pronto_para_renderizacao
            ),

            "renderizado": False,

            "tipo": (
                "avatar_proporcional"
            ),

            "motor_renderizacao": None,
        },

        "entrada_usuario": {
            "altura_obrigatoria": False,
            "peso_obrigatorio": False,
            "cintura_obrigatoria": False,
            "medidas_manuais_obrigatorias": False,
        },

        "capacidades": {
            "representacao_corporal": True,

            "avatar_proporcional": (
                pronto_para_renderizacao
            ),

            "comparacao_visual": (
                estrutura_completa
            ),

            "vestir_produto_virtualmente": False,

            "gerar_imagem_realista": False,

            "recomendar_tamanho_diretamente": False,
        },

        "gerado": False,

        "experimental": True,

        "mensagem": (
            "Avatar Corporal V1 preparado "
            "a partir da representação visual "
            "do corpo. Nenhuma altura física, "
            "peso ou medida antropométrica "
            "foi inferida."
        ),
    }