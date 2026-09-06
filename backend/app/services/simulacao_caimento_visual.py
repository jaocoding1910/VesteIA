from app.services.categorias_vestuario import (
    normalizar_categoria,
    obter_familia_categoria,
)


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
    Normaliza textos utilizados
    pelas regras visuais.
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


# ==========================================================
# MODELAGEM
# ==========================================================

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
        "ajustado": 0.96,
        "justa": 0.96,
        "justo": 0.96,

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
        "padrão": 1.00,
        "normal": 1.00,
        "regular": 1.00,
        "solto": 1.05,
        "amplo": 1.05,
        "oversized": 1.05,
    }

    return mapa.get(
        preferencia,
        1.00,
    )


def _classificar_caimento_visual(
    fator_visual,
):
    """
    Classifica a tendência visual
    da transformação aplicada.
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


# ==========================================================
# TRANSFORMAÇÃO
# ==========================================================

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

    Não representa simulação física
    de tecido.
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


# ==========================================================
# VALIDAÇÃO POR FAMÍLIA
# ==========================================================

def _regiao_disponivel(
    regioes,
    nome,
):
    """
    Verifica se uma região visual
    está disponível.
    """

    return bool(
        (
            regioes.get(
                nome,
                {},
            )
            or {}
        ).get(
            "disponivel",
            False,
        )
    )


def _avaliar_estrutura_familia(
    familia,
    categoria,
    regioes,
):
    """
    Valida a geometria de caimento
    conforme a família da vestimenta.

    Essa função é o ponto principal
    da generalização multivestimenta.
    """

    tronco_disponivel = (
        _regiao_disponivel(
            regioes,
            "tronco",
        )
    )

    cintura_quadril_disponivel = (
        _regiao_disponivel(
            regioes,
            "cintura_quadril",
        )
    )

    perna_esquerda_disponivel = (
        _regiao_disponivel(
            regioes,
            "perna_esquerda",
        )
    )

    perna_direita_disponivel = (
        _regiao_disponivel(
            regioes,
            "perna_direita",
        )
    )

    pernas_disponiveis = (
        perna_esquerda_disponivel
        and perna_direita_disponivel
    )

    saia_disponivel = (
        _regiao_disponivel(
            regioes,
            "saia",
        )
    )

    corpo_integrado_disponivel = (
        _regiao_disponivel(
            regioes,
            "corpo_integrado",
        )
    )

    pe_esquerdo_disponivel = (
        _regiao_disponivel(
            regioes,
            "pe_esquerdo",
        )
    )

    pe_direito_disponivel = (
        _regiao_disponivel(
            regioes,
            "pe_direito",
        )
    )

    pes_disponiveis = (
        pe_esquerdo_disponivel
        and pe_direito_disponivel
    )

    # ======================================================
    # SUPERIOR
    # ======================================================

    if familia == "superior":
        regiao_principal = (
            "tronco"
        )

        regiao_principal_disponivel = (
            tronco_disponivel
        )

        estrutura_familia_disponivel = (
            tronco_disponivel
        )

    # ======================================================
    # INFERIOR
    # ======================================================

    elif familia == "inferior":

        if categoria == "saia":
            regiao_principal = (
                "saia"
            )

            regiao_principal_disponivel = (
                saia_disponivel
            )

            estrutura_familia_disponivel = (
                saia_disponivel
            )

        else:
            regiao_principal = (
                "cintura_quadril"
            )

            regiao_principal_disponivel = (
                cintura_quadril_disponivel
            )

            estrutura_familia_disponivel = (
                cintura_quadril_disponivel
                and pernas_disponiveis
            )

    # ======================================================
    # CORPO INTEGRADO
    # ======================================================

    elif familia == "corpo_integrado":
        regiao_principal = (
            "corpo_integrado"
        )

        regiao_principal_disponivel = (
            corpo_integrado_disponivel
        )

        estrutura_familia_disponivel = (
            corpo_integrado_disponivel
        )

    # ======================================================
    # CALÇADO
    # ======================================================

    elif familia == "calcado":
        regiao_principal = (
            "pes"
        )

        regiao_principal_disponivel = (
            pes_disponiveis
        )

        estrutura_familia_disponivel = (
            pes_disponiveis
        )

    else:
        regiao_principal = None

        regiao_principal_disponivel = (
            False
        )

        estrutura_familia_disponivel = (
            False
        )

    return {
        "familia": (
            familia
        ),

        "categoria": (
            categoria
        ),

        "regiao_principal": (
            regiao_principal
        ),

        "regiao_principal_disponivel": (
            regiao_principal_disponivel
        ),

        "tronco_disponivel": (
            tronco_disponivel
        ),

        "cintura_quadril_disponivel": (
            cintura_quadril_disponivel
        ),

        "perna_esquerda_disponivel": (
            perna_esquerda_disponivel
        ),

        "perna_direita_disponivel": (
            perna_direita_disponivel
        ),

        "pernas_disponiveis": (
            pernas_disponiveis
        ),

        "saia_disponivel": (
            saia_disponivel
        ),

        "corpo_integrado_disponivel": (
            corpo_integrado_disponivel
        ),

        "pe_esquerdo_disponivel": (
            pe_esquerdo_disponivel
        ),

        "pe_direito_disponivel": (
            pe_direito_disponivel
        ),

        "pes_disponiveis": (
            pes_disponiveis
        ),

        "estrutura_familia_disponivel": (
            estrutura_familia_disponivel
        ),
    }


# ==========================================================
# FUNÇÃO PRINCIPAL
# ==========================================================

def simular_caimento_visual_v1(
    vestimenta_avatar_2d: dict,
    representacao_roupa: dict,
    preferencia_caimento: str,
):
    """
    Gera a Simulação Visual de Caimento V1.

    Sprint Multivestimenta.

    Esta camada recebe:
    - roupa posicionada no avatar;
    - representação da peça;
    - categoria e família;
    - preferência visual de caimento.

    IMPORTANTE:

    Esta função NÃO:
    - simula física real de tecido;
    - calcula gravidade;
    - calcula colisão;
    - calcula elasticidade real;
    - estima circunferências;
    - calcula folga real em centímetros;
    - converte corpo para centímetros;
    - recomenda tamanho;
    - altera calibração corporal.

    O resultado continua sendo uma
    interpretação visual experimental.
    """

    # ======================================================
    # VESTIMENTA
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
    # REPRESENTAÇÃO
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
    # PRODUTO / CATEGORIA
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
            or vestimenta_avatar_2d.get(
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
        or vestimenta_avatar_2d.get(
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
                "simulacao_caimento_visual_v1"
            ),

            "status": (
                "categoria_ou_familia_indisponivel"
            ),

            "disponivel": False,

            "caimento_simulado": False,

            "pronta_para_renderizacao_final": False,
        }

    # ======================================================
    # MODELAGEM
    # ======================================================

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
    # TRANSFORMAÇÃO VISUAL
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

    # A transformação vertical permanece
    # propositalmente conservadora.
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
    # PONTOS
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

    # ======================================================
    # CALÇADO
    #
    # A ancoragem dos pés não possui um único
    # centro global como tronco/quadril.
    #
    # Portanto usamos o centro médio dos pontos
    # apenas como pivô da transformação visual.
    # ======================================================

    if (
        centro_x is None
        or ancora_y is None
    ):
        coordenadas_validas = [
            ponto
            for ponto in pontos_origem.values()
            if (
                isinstance(
                    ponto,
                    dict,
                )
                and _numero(
                    ponto.get(
                        "x"
                    )
                )
                is not None
                and _numero(
                    ponto.get(
                        "y"
                    )
                )
                is not None
            )
        ]

        if coordenadas_validas:
            centro_x = (
                sum(
                    ponto["x"]
                    for ponto in coordenadas_validas
                )
                / len(
                    coordenadas_validas
                )
            )

            ancora_y = (
                min(
                    ponto["y"]
                    for ponto in coordenadas_validas
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

            "categoria": (
                categoria
            ),

            "familia": (
                familia
            ),

            "caimento_simulado": False,

            "pronta_para_renderizacao_final": False,
        }

    # ======================================================
    # DEFORMAÇÃO
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
                ponto=(
                    ponto
                ),

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
    # QUALIDADE DOS PONTOS
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

    # ======================================================
    # ESTRUTURA DA FAMÍLIA
    # ======================================================

    estrutura = (
        _avaliar_estrutura_familia(
            familia=(
                familia
            ),

            categoria=(
                categoria
            ),

            regioes=(
                regioes_caimento
            ),
        )
    )

    estrutura_familia_disponivel = (
        estrutura.get(
            "estrutura_familia_disponivel",
            False,
        )
    )

    simulacao_pronta = (
        estrutura_familia_disponivel
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
    # SAÍDA
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

        "categoria": (
            categoria
        ),

        "familia": (
            familia
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

            "ancora_y": (
                _arredondar(
                    ancora_y
                )
            ),

            # Compatibilidade com contrato V1.
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
            "transformacao_horizontal": (
                fator_horizontal
            ),

            "transformacao_vertical": (
                fator_vertical
            ),

            "familia_validada": (
                familia
            ),

            "estrutura_familia_disponivel": (
                estrutura_familia_disponivel
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

            **estrutura,
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
                "visualmente conforme a modelagem, "
                "a preferência de caimento e a "
                "família estrutural da vestimenta."
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

            "multivestimenta": True,

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
            "gerada a partir da roupa posicionada "
            "no Avatar 2D e validada conforme a "
            "família da vestimenta. O resultado "
            "representa uma tendência visual "
            "experimental e não uma simulação "
            "física real de tecido."
        ),
    }