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


def _normalizar_texto(
    valor,
):
    """
    Normaliza textos usados
    nas regras visuais.
    """

    if valor is None:
        return ""

    return (
        str(
            valor
        )
        .strip()
        .lower()
    )


def _obter_fator_modelagem(
    modelagem,
):
    """
    Retorna um fator VISUAL de expansão
    baseado na modelagem cadastrada.

    Não representa folga física em cm.
    """

    modelagem = (
        _normalizar_texto(
            modelagem
        )
    )

    mapa = {
        "slim": 0.96,
        "ajustada": 0.96,
        "justa": 0.96,

        "regular": 1.00,
        "tradicional": 1.00,
        "normal": 1.00,

        "oversized": 1.08,
        "ampla": 1.08,
        "amplo": 1.08,
    }

    return mapa.get(
        modelagem,
        1.00,
    )


def _obter_fator_preferencia(
    preferencia_caimento,
):
    """
    Retorna um fator VISUAL associado
    à preferência escolhida pelo usuário.

    Não representa medida física.
    """

    preferencia = (
        _normalizar_texto(
            preferencia_caimento
        )
    )

    mapa = {
        "justo": 0.97,
        "padrao": 1.00,
        "solto": 1.05,
    }

    return mapa.get(
        preferencia,
        1.00,
    )


def _classificar_caimento_visual(
    fator_visual,
):
    """
    Classifica o resultado visual
    da expansão aplicada.
    """

    fator_visual = (
        _numero(
            fator_visual
        )
    )

    if fator_visual is None:
        return "indisponivel"

    if fator_visual < 0.99:
        return "mais_ajustado"

    if fator_visual <= 1.03:
        return "equilibrado"

    if fator_visual <= 1.10:
        return "solto"

    return "amplo"


def _transformar_ponto_caimento(
    ponto,
    centro_x,
    ancora_y,
    fator_horizontal,
    fator_vertical,
):
    """
    Aplica deformação VISUAL simples
    à roupa já posicionada.

    A transformação acontece ao redor
    do centro horizontal da peça e de
    uma âncora vertical próxima aos ombros.

    Não é simulação física de tecido.
    """

    if not isinstance(
        ponto,
        dict,
    ):
        return None

    x = (
        _numero(
            ponto.get(
                "x"
            )
        )
    )

    y = (
        _numero(
            ponto.get(
                "y"
            )
        )
    )

    if (
        x is None
        or y is None
    ):
        return None

    novo_x = (
        centro_x
        + (
            x
            - centro_x
        )
        * fator_horizontal
    )

    novo_y = (
        ancora_y
        + (
            y
            - ancora_y
        )
        * fator_vertical
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
            "vestimenta_avatar_2d_v1"
        ),
    }


def simular_caimento_visual_v1(
    vestimenta_avatar_2d: dict,
    representacao_roupa: dict,
    preferencia_caimento: str,
):
    """
    Gera a Simulação Visual de Caimento V1.

    Esta camada recebe:
    - a roupa já posicionada no avatar;
    - a representação da roupa;
    - a preferência visual de caimento.

    O objetivo é produzir uma geometria
    visual deformada de forma controlada
    para representar tendências de
    caimento.

    IMPORTANTE:

    Esta função NÃO:
    - simula física real de tecido;
    - calcula gravidade;
    - calcula colisão física;
    - calcula elasticidade real;
    - estima circunferência corporal;
    - calcula folga real em centímetros;
    - converte corpo para centímetros;
    - recomenda tamanho;
    - altera a Sprint 48;
    - afirma ajuste físico exato.

    O resultado é uma interpretação
    visual experimental.
    """

    # ======================================================
    # VALIDAÇÃO DA VESTIMENTA
    # ======================================================

    if not isinstance(
        vestimenta_avatar_2d,
        dict,
    ):
        return {
            "versao": (
                "simulacao_caimento_visual_v1"
            ),

            "status": (
                "vestimenta_invalida"
            ),

            "disponivel": False,

            "caimento_simulado": False,

            "pronta_para_renderizacao_final": False,
        }

    if not vestimenta_avatar_2d.get(
        "pronta_para_simulacao_caimento",
        False,
    ):
        return {
            "versao": (
                "simulacao_caimento_visual_v1"
            ),

            "status": (
                "vestimenta_nao_pronta"
            ),

            "disponivel": False,

            "caimento_simulado": False,

            "pronta_para_renderizacao_final": False,
        }

    # ======================================================
    # VALIDAÇÃO DA REPRESENTAÇÃO DA ROUPA
    # ======================================================

    if not isinstance(
        representacao_roupa,
        dict,
    ):
        return {
            "versao": (
                "simulacao_caimento_visual_v1"
            ),

            "status": (
                "representacao_roupa_invalida"
            ),

            "disponivel": False,

            "caimento_simulado": False,

            "pronta_para_renderizacao_final": False,
        }

    # ======================================================
    # PRODUTO / MODELAGEM
    # ======================================================

    produto = (
        representacao_roupa.get(
            "produto"
        )
        or {}
    )

    modelagem = (
        produto.get(
            "modelagem"
        )
    )

    fator_modelagem = (
        _obter_fator_modelagem(
            modelagem
        )
    )

    fator_preferencia = (
        _obter_fator_preferencia(
            preferencia_caimento
        )
    )

    # ======================================================
    # FATOR VISUAL FINAL
    # ======================================================

    fator_horizontal = (
        fator_modelagem
        * fator_preferencia
    )

    fator_horizontal = (
        _arredondar(
            fator_horizontal
        )
    )

    # Mantemos a deformação vertical
    # mais conservadora.
    #
    # Isso evita transformar uma preferência
    # "solta" em um falso comprimento físico.
    fator_vertical = (
        1.0
        + (
            fator_horizontal
            - 1.0
        )
        * 0.25
    )

    fator_vertical = (
        _arredondar(
            fator_vertical
        )
    )

    classificacao = (
        _classificar_caimento_visual(
            fator_horizontal
        )
    )

    # ======================================================
    # PONTOS DA ROUPA JÁ POSICIONADA
    # ======================================================

    pontos_origem = (
        vestimenta_avatar_2d.get(
            "pontos_roupa_no_avatar"
        )
        or {}
    )

    ancoragem = (
        vestimenta_avatar_2d.get(
            "ancoragem"
        )
        or {}
    )

    centro_x = (
        _numero(
            ancoragem.get(
                "centro_avatar_x"
            )
        )
    )

    ancora_y = (
        _numero(
            ancoragem.get(
                "centro_avatar_y"
            )
        )
    )

    if (
        centro_x is None
        or ancora_y is None
    ):
        return {
            "versao": (
                "simulacao_caimento_visual_v1"
            ),

            "status": (
                "ancoragem_indisponivel"
            ),

            "disponivel": False,

            "caimento_simulado": False,

            "pronta_para_renderizacao_final": False,
        }

    # ======================================================
    # DEFORMAÇÃO VISUAL
    # ======================================================

    pontos_caimento = {}

    for (
        nome,
        ponto,
    ) in pontos_origem.items():

        pontos_caimento[
            nome
        ] = (
            _transformar_ponto_caimento(
                ponto=ponto,

                centro_x=(
                    centro_x
                ),

                ancora_y=(
                    ancora_y
                ),

                fator_horizontal=(
                    fator_horizontal
                ),

                fator_vertical=(
                    fator_vertical
                ),
            )
        )

    # ======================================================
    # REGIÕES
    # ======================================================

    regioes_origem = (
        vestimenta_avatar_2d.get(
            "regioes"
        )
        or {}
    )

    regioes_caimento = {}

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
            pontos_caimento.get(
                nome
            )
            is not None
            for nome in nomes_pontos
        )

        regioes_caimento[
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
    # VALIDAÇÃO VISUAL DA LARGURA
    # ======================================================

    ombro_esquerdo = (
        pontos_caimento.get(
            "ombro_esquerdo"
        )
    )

    ombro_direito = (
        pontos_caimento.get(
            "ombro_direito"
        )
    )

    largura_ombros_caimento = None

    if (
        isinstance(
            ombro_esquerdo,
            dict,
        )
        and isinstance(
            ombro_direito,
            dict,
        )
    ):
        largura_ombros_caimento = abs(
            ombro_esquerdo[
                "x"
            ]
            - ombro_direito[
                "x"
            ]
        )

        largura_ombros_caimento = (
            _arredondar(
                largura_ombros_caimento
            )
        )

    # ======================================================
    # QUALIDADE
    # ======================================================

    total_pontos = len(
        pontos_caimento
    )

    pontos_disponiveis = sum(
        ponto is not None
        for ponto in (
            pontos_caimento.values()
        )
    )

    percentual_pontos = (
        pontos_disponiveis
        / total_pontos
        if total_pontos
        else 0
    )

    tronco_disponivel = (
        regioes_caimento
        .get(
            "tronco",
            {},
        )
        .get(
            "disponivel",
            False,
        )
    )

    simulacao_pronta = (
        tronco_disponivel
        and percentual_pontos >= 0.80
    )

    if simulacao_pronta:
        status = (
            "caimento_visual_simulado"
        )

    elif pontos_disponiveis > 0:
        status = (
            "caimento_visual_parcial"
        )

    else:
        status = (
            "caimento_visual_indisponivel"
        )

    # ======================================================
    # SAÍDA FINAL
    # ======================================================

    return {
        "versao": (
            "simulacao_caimento_visual_v1"
        ),

        "status": (
            status
        ),

        "disponivel": (
            pontos_disponiveis > 0
        ),

        "origem": {
            "vestimenta": (
                "vestimenta_avatar_2d_v1"
            ),

            "roupa": (
                "representacao_roupa_v1"
            ),
        },

        "produto": (
            produto
        ),

        "preferencia_caimento": (
            preferencia_caimento
        ),

        "modelagem": (
            modelagem
        ),

        "parametros_visuais": {
            "fator_modelagem": (
                _arredondar(
                    fator_modelagem
                )
            ),

            "fator_preferencia": (
                _arredondar(
                    fator_preferencia
                )
            ),

            "fator_horizontal_final": (
                fator_horizontal
            ),

            "fator_vertical_final": (
                fator_vertical
            ),

            "classificacao_visual": (
                classificacao
            ),

            "usa_centimetros_corpo": False,

            "representa_folga_fisica": False,
        },

        "ancoragem": {
            "centro_x": (
                _arredondar(
                    centro_x
                )
            ),

            "ombros_y": (
                _arredondar(
                    ancora_y
                )
            ),

            "preservada": True,
        },

        "pontos_caimento": (
            pontos_caimento
        ),

        "regioes": (
            regioes_caimento
        ),

        "validacao_visual": {
            "largura_ombros_resultante": (
                largura_ombros_caimento
            ),

            "transformacao_horizontal": (
                fator_horizontal
            ),

            "transformacao_vertical": (
                fator_vertical
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

        "interpretacao": {
            "tipo": (
                "tendencia_visual"
            ),

            "resultado": (
                classificacao
            ),

            "descricao": (
                "A geometria da peça foi ajustada "
                "visualmente conforme a modelagem "
                "cadastrada e a preferência de "
                "caimento selecionada."
            ),
        },

        "capacidades": {
            "caimento_visual_disponivel": (
                simulacao_pronta
            ),

            "roupa_deformada_visualmente": (
                simulacao_pronta
            ),

            "pronta_para_renderizacao_final": (
                simulacao_pronta
            ),

            "simulacao_fisica_tecido": False,

            "imagem_final_gerada": False,
        },

        "restricoes": {
            "usa_centimetros_corpo": False,

            "calcula_folga_cm": False,

            "simula_gravidade": False,

            "simula_colisao": False,

            "simula_elasticidade_real": False,

            "recomenda_tamanho": False,

            "representa_ajuste_fisico_exato": False,
        },

        "caimento_simulado": (
            simulacao_pronta
        ),

        "pronta_para_renderizacao_final": (
            simulacao_pronta
        ),

        "imagem_gerada": False,

        "experimental": True,

        "mensagem": (
            "Simulação Visual de Caimento V1 "
            "gerada a partir da roupa já posicionada "
            "no Avatar 2D. O resultado representa "
            "uma tendência visual experimental e "
            "não uma simulação física real de tecido."
        ),
    }