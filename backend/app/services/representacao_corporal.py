def _obter_valor(
    dados: dict,
    chave: str,
    padrao=None,
):
    """
    Recupera um valor de um dicionário
    de forma segura.
    """

    if not isinstance(dados, dict):
        return padrao

    return dados.get(
        chave,
        padrao,
    )


def _arredondar(
    valor,
    casas=4,
):
    """
    Arredonda valores numéricos
    quando disponíveis.
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


def gerar_representacao_corporal_v1(
    deteccao: dict,
):
    """
    Gera a representação corporal visual
    oficial do VesteIA para o fluxo foto-first.

    Esta camada NÃO:
    - estima altura física;
    - inventa centímetros;
    - recalcula o Sprint 48;
    - recomenda tamanho;
    - altera calibração;
    - altera ranking.

    Ela organiza apenas informações
    realmente observáveis na fotografia.

    A representação poderá ser consumida
    futuramente por:
    - Avatar VesteIA;
    - comparação visual;
    - modelos foto-only;
    - geração visual de vestuário.
    """

    if not isinstance(
        deteccao,
        dict,
    ):
        return {
            "versao": "representacao_corporal_v1",
            "status": "indisponivel",
            "disponivel": False,
            "origem": "foto",
            "pronta_para_avatar": False,
            "experimental": True,
            "mensagem": (
                "A detecção corporal não está "
                "disponível para gerar a "
                "representação visual."
            ),
        }

    # ======================================================
    # PRESENÇA HUMANA
    # ======================================================

    pessoa_detectada = bool(
        deteccao.get(
            "pessoa_detectada",
            False,
        )
    )

    if not pessoa_detectada:
        return {
            "versao": "representacao_corporal_v1",
            "status": "pessoa_nao_detectada",
            "disponivel": False,
            "origem": "foto",
            "pronta_para_avatar": False,
            "experimental": True,
            "mensagem": (
                "Nenhuma pessoa foi detectada "
                "na fotografia."
            ),
        }

    # ======================================================
    # FONTES
    # ======================================================

    geometria = (
        deteccao.get(
            "geometria_corporal"
        )
        or {}
    )

    proporcoes = (
        deteccao.get(
            "proporcoes_corporais"
        )
        or {}
    )

    interpretacao = (
        deteccao.get(
            "interpretacao_corporal"
        )
        or {}
    )

    referencia_altura = (
        deteccao.get(
            "referencia_altura_corporal"
        )
        or {}
    )

    qualidade_captura = (
        deteccao.get(
            "qualidade_captura"
        )
        or {}
    )

    consistencia = (
        deteccao.get(
            "consistencia_geometrica"
        )
        or {}
    )

    pose = (
        deteccao.get(
            "pose_para_correcao_anatomica"
        )
        or {}
    )

    distorcao = (
        deteccao.get(
            "indice_distorcao_perspectiva"
        )
        or {}
    )

    escala_corporal = (
        deteccao.get(
            "escala_corporal"
        )
        or {}
    )

    # ======================================================
    # GEOMETRIA VISUAL
    # ======================================================

    largura_ombros = (
        _arredondar(
            geometria.get(
                "largura_ombros"
            )
        )
    )

    largura_quadril = (
        _arredondar(
            geometria.get(
                "largura_quadril"
            )
        )
    )

    largura_torax = (
        _arredondar(
            geometria.get(
                "largura_torax_relativa"
            )
        )
    )

    comprimento_tronco = (
        _arredondar(
            geometria.get(
                "comprimento_tronco_relativo"
            )
        )
    )

    altura_corpo_relativa = (
        _arredondar(
            referencia_altura.get(
                "altura_corpo_relativa"
            )
        )
    )

    # ======================================================
    # PROPORÇÕES
    # ======================================================

    proporcao_ombros_quadril = (
        _arredondar(
            proporcoes.get(
                "proporcao_ombros_quadril"
            )
        )
    )

    relacao_ombros_quadril = (
        interpretacao.get(
            "relacao_ombros_quadril"
        )
    )

    # ======================================================
    # QUALIDADE VISUAL
    # ======================================================

    qualidade_nivel = (
        qualidade_captura.get(
            "nivel",
            "indisponivel",
        )
    )

    qualidade_pontuacao = (
        _arredondar(
            qualidade_captura.get(
                "pontuacao"
            )
        )
    )

    geometria_consistente = bool(
        consistencia.get(
            "consistente",
            False,
        )
    )

    pose_apta = bool(
        pose.get(
            "pose_apta",
            False,
        )
    )

    nivel_distorcao = (
        distorcao.get(
            "nivel_distorcao",
            "indisponivel",
        )
    )

    # ======================================================
    # ESCALA FÍSICA
    # ======================================================

    escala_fisica_disponivel = bool(
        escala_corporal.get(
            "conversao_disponivel",
            False,
        )
    )

    # ======================================================
    # COMPLETUDE DA GEOMETRIA
    # ======================================================

    valores_geometria = (
        largura_ombros,
        largura_quadril,
        largura_torax,
        comprimento_tronco,
        altura_corpo_relativa,
    )

    quantidade_geometria = sum(
        valor is not None
        for valor in valores_geometria
    )

    geometria_visual_completa = (
        quantidade_geometria
        == len(
            valores_geometria
        )
    )

    # ======================================================
    # CORPO INTEIRO
    # ======================================================

    calibracao_corporal = (
        deteccao.get(
            "calibracao_corporal"
        )
        or {}
    )

    corpo_inteiro_visivel = bool(
        calibracao_corporal.get(
            "corpo_inteiro_visivel",
            False,
        )
    )

    # ======================================================
    # APTIDÃO PARA AVATAR
    # ======================================================

    pronta_para_avatar = (
        pessoa_detectada
        and geometria_visual_completa
        and geometria_consistente
        and pose_apta
        and qualidade_nivel
        in (
            "boa",
            "excelente",
        )
    )

    # ======================================================
    # STATUS
    # ======================================================

    if pronta_para_avatar:
        status = (
            "representacao_visual_pronta"
        )

    elif quantidade_geometria > 0:
        status = (
            "representacao_visual_parcial"
        )

    else:
        status = (
            "geometria_visual_indisponivel"
        )

    # ======================================================
    # RESULTADO
    # ======================================================

    return {
        "versao": (
            "representacao_corporal_v1"
        ),

        "status": status,

        "disponivel": (
            quantidade_geometria > 0
        ),

        "origem": "foto",

        "corpo": {
            "pessoa_detectada": (
                pessoa_detectada
            ),

            "corpo_inteiro_visivel": (
                corpo_inteiro_visivel
            ),

            "landmarks_detectados": (
                deteccao.get(
                    "landmarks_detectados",
                    0,
                )
            ),
        },

        "geometria_visual": {
            "largura_ombros_relativa": (
                largura_ombros
            ),

            "largura_quadril_relativa": (
                largura_quadril
            ),

            "largura_torax_relativa": (
                largura_torax
            ),

            "comprimento_tronco_relativo": (
                comprimento_tronco
            ),

            "altura_corpo_relativa": (
                altura_corpo_relativa
            ),

            "unidade": (
                "coordenadas_normalizadas_corrigidas"
            ),

            "completa": (
                geometria_visual_completa
            ),
        },

        "proporcoes": {
            "ombros_quadril": (
                proporcao_ombros_quadril
            ),

            "relacao_ombros_quadril": (
                relacao_ombros_quadril
            ),
        },

        "qualidade_visual": {
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

            "nivel_distorcao": (
                nivel_distorcao
            ),
        },

        "escala_fisica": {
            "disponivel": (
                escala_fisica_disponivel
            ),

            "origem": (
                "calibracao_externa"
                if escala_fisica_disponivel
                else "indisponivel"
            ),

            "centimetros_disponiveis": (
                escala_fisica_disponivel
            ),

            "altura_fisica_inferida": False,

            "mensagem": (
                (
                    "Existe uma referência física "
                    "disponível para conversão."
                )
                if escala_fisica_disponivel
                else
                (
                    "A fotografia foi analisada "
                    "sem inferir uma altura física "
                    "ou converter a geometria "
                    "corporal para centímetros."
                )
            ),
        },

        "avatar": {
            "pronta_para_avatar": (
                pronta_para_avatar
            ),

            "gerado": False,

            "modo": (
                "representacao_corporal_visual"
            ),

            "necessita_altura_manual": False,

            "necessita_peso_manual": False,

            "necessita_cintura_manual": False,
        },

        "uso": {
            "analise_visual": True,

            "avatar": (
                pronta_para_avatar
            ),

            "comparacao_proporcional": (
                geometria_visual_completa
            ),

            "comparacao_fisica_cm": (
                escala_fisica_disponivel
            ),

            "recomendacao_dimensional_direta": False,
        },

        "experimental": True,

        "mensagem": (
            "Representação corporal visual "
            "gerada a partir da fotografia. "
            "Os valores representam geometria "
            "relativa observada e não medidas "
            "antropométricas em centímetros."
        ),
    }