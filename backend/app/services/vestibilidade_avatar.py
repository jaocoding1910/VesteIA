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
        return float(valor)

    except (
        TypeError,
        ValueError,
    ):
        return None


def _limitar(
    valor,
    minimo,
    maximo,
):
    """
    Mantém um valor dentro
    de um intervalo seguro.
    """

    valor = _numero(valor)

    if valor is None:
        return None

    return max(
        minimo,
        min(
            maximo,
            valor,
        ),
    )


def _arredondar(
    valor,
    casas=4,
):
    """
    Arredonda valores numéricos
    de forma segura.
    """

    valor = _numero(valor)

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
    pelas regras da vestibilidade.
    """

    if valor is None:
        return ""

    return (
        str(valor)
        .strip()
        .lower()
    )


# ==========================================================
# PERFIL CORPORAL DO AVATAR
# ==========================================================

def _fator_altura(
    altura_cm,
):
    """
    Converte a altura aproximada
    informada pelo usuário em uma
    escala visual relativa.

    Referência visual:
    175 cm = 1.0

    Não representa medição corporal.
    """

    altura = (
        _numero(
            altura_cm
        )
        or 175.0
    )

    fator = (
        altura
        / 175.0
    )

    return _limitar(
        fator,
        0.84,
        1.16,
    )


def _fator_peso(
    peso_kg,
):
    """
    Produz uma tendência visual
    de largura baseada no peso
    aproximado informado.

    Não converte peso em
    circunferências corporais.
    """

    peso = (
        _numero(
            peso_kg
        )
        or 75.0
    )

    fator = (
        1.0
        + (
            peso
            - 75.0
        )
        * 0.0032
    )

    return _limitar(
        fator,
        0.82,
        1.23,
    )


def _fator_porte(
    porte_corporal,
):
    """
    Retorna a influência visual
    do porte corporal selecionado.
    """

    porte = (
        _normalizar_texto(
            porte_corporal
        )
    )

    mapa = {
        "estreito": 0.90,
        "medio": 1.00,
        "médio": 1.00,
        "largo": 1.10,
    }

    return mapa.get(
        porte,
        1.00,
    )


def _fator_tronco(
    proporcao_tronco,
):
    """
    Retorna a escala visual
    relativa do tronco.
    """

    proporcao = (
        _normalizar_texto(
            proporcao_tronco
        )
    )

    mapa = {
        "curto": 0.90,
        "media": 1.00,
        "média": 1.00,
        "medio": 1.00,
        "médio": 1.00,
        "longo": 1.10,
    }

    return mapa.get(
        proporcao,
        1.00,
    )


def _fator_pernas(
    proporcao_pernas,
):
    """
    Retorna a escala visual
    relativa das pernas.
    """

    proporcao = (
        _normalizar_texto(
            proporcao_pernas
        )
    )

    mapa = {
        "curtas": 0.90,
        "curta": 0.90,

        "media": 1.00,
        "média": 1.00,
        "medias": 1.00,
        "médias": 1.00,

        "longas": 1.10,
        "longa": 1.10,
    }

    return mapa.get(
        proporcao,
        1.00,
    )


def _fator_genero_ombros(
    genero,
):
    """
    Diferencia somente a
    silhueta visual base.

    Não representa inferência
    anatômica automática.
    """

    genero = (
        _normalizar_texto(
            genero
        )
    )

    if genero == "feminino":
        return 0.94

    return 1.00


def _fator_genero_quadril(
    genero,
):
    """
    Diferencia somente a
    silhueta visual base.
    """

    genero = (
        _normalizar_texto(
            genero
        )
    )

    if genero == "feminino":
        return 1.10

    return 1.00


# ==========================================================
# CLASSIFICAÇÃO DA VESTIBILIDADE
# ==========================================================

def _classificar_vestibilidade(
    fator_relativo_roupa,
):
    """
    Classifica como a peça tende
    a parecer no avatar.

    Quanto menor o fator,
    maior a tendência de ajuste.

    Quanto maior,
    maior a tendência de folga.

    É uma classificação VISUAL.
    """

    fator = (
        _numero(
            fator_relativo_roupa
        )
    )

    if fator is None:
        return "indisponivel"

    if fator < 0.94:
        return "mais_justo"

    if fator < 0.99:
        return "ajustado"

    if fator <= 1.03:
        return "equilibrado"

    if fator <= 1.08:
        return "folgado"

    return "amplo"


# ==========================================================
# FUNÇÃO PRINCIPAL
# ==========================================================

def gerar_vestibilidade_avatar_v1(
    perfil_avatar: dict,
    produto: dict | None = None,
    tamanho_selecionado=None,
):
    """
    Gera a Vestibilidade Visual do Avatar V1.

    Sprint 53 — Vestibilidade Dinâmica.

    Entrada:
    - perfil aproximado criado no AvatarBuilder;
    - produto selecionado;
    - tamanho/variante selecionado.

    Esta camada considera:
    - gênero visual escolhido;
    - altura aproximada;
    - peso aproximado;
    - porte corporal;
    - proporção do tronco;
    - proporção das pernas.

    IMPORTANTE:

    Esta função NÃO:
    - mede o corpo;
    - estima circunferências reais;
    - converte peso em centímetros;
    - calcula folga física;
    - simula tecido;
    - recomenda tamanho;
    - afirma que uma peça realmente servirá.

    O resultado representa somente
    uma tendência visual utilizada
    pelo renderer do VesteIA.
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if not isinstance(
        perfil_avatar,
        dict,
    ):
        return {
            "versao": (
                "vestibilidade_avatar_v1"
            ),

            "status": (
                "perfil_avatar_invalido"
            ),

            "disponivel": False,

            "vestibilidade_calculada": False,

            "mensagem": (
                "O perfil do avatar "
                "recebido é inválido."
            ),
        }


    produto = (
        produto
        if isinstance(
            produto,
            dict,
        )
        else {}
    )


    # ======================================================
    # DADOS DO AVATAR
    # ======================================================

    genero = (
        _normalizar_texto(
            perfil_avatar.get(
                "genero"
            )
        )
        or "masculino"
    )

    if genero not in {
        "masculino",
        "feminino",
    }:
        genero = "masculino"


    altura_cm = (
        _numero(
            perfil_avatar.get(
                "altura_aproximada_cm"
            )
        )
        or 175.0
    )


    peso_kg = (
        _numero(
            perfil_avatar.get(
                "peso_aproximado_kg"
            )
        )
        or 75.0
    )


    porte_corporal = (
        _normalizar_texto(
            perfil_avatar.get(
                "porte_corporal"
            )
        )
        or "medio"
    )


    proporcao_tronco = (
        _normalizar_texto(
            perfil_avatar.get(
                "proporcao_tronco"
            )
        )
        or "media"
    )


    proporcao_pernas = (
        _normalizar_texto(
            perfil_avatar.get(
                "proporcao_pernas"
            )
        )
        or "media"
    )


    # ======================================================
    # FATORES CORPORAIS
    # ======================================================

    fator_altura = (
        _fator_altura(
            altura_cm
        )
    )


    fator_peso = (
        _fator_peso(
            peso_kg
        )
    )


    fator_porte = (
        _fator_porte(
            porte_corporal
        )
    )


    fator_tronco = (
        _fator_tronco(
            proporcao_tronco
        )
    )


    fator_pernas = (
        _fator_pernas(
            proporcao_pernas
        )
    )


    fator_genero_ombros = (
        _fator_genero_ombros(
            genero
        )
    )


    fator_genero_quadril = (
        _fator_genero_quadril(
            genero
        )
    )


    # ======================================================
    # LARGURA CORPORAL VISUAL
    # ======================================================

    fator_largura_corpo = (
        fator_peso
        * fator_porte
    )

    fator_largura_corpo = (
        _limitar(
            fator_largura_corpo,
            0.78,
            1.30,
        )
    )


    # ======================================================
    # OMBROS / QUADRIL
    # ======================================================

    fator_ombros = (
        fator_porte
        * fator_genero_ombros
    )

    fator_ombros = (
        _limitar(
            fator_ombros,
            0.82,
            1.22,
        )
    )


    fator_quadril = (
        fator_porte
        * fator_genero_quadril
    )

    fator_quadril = (
        _limitar(
            fator_quadril,
            0.85,
            1.25,
        )
    )


    # ======================================================
    # RELAÇÃO ROUPA × CORPO
    #
    # Corpo visualmente maior:
    # a mesma roupa tende a parecer
    # relativamente mais ajustada.
    #
    # Corpo visualmente menor:
    # a mesma roupa tende a parecer
    # relativamente mais folgada.
    #
    # Não representa folga física.
    # ======================================================

    if (
        fator_largura_corpo
        and fator_largura_corpo > 0
    ):
        fator_horizontal_relativo = (
            1.0
            / fator_largura_corpo
        )

    else:
        fator_horizontal_relativo = 1.0


    fator_horizontal_relativo = (
        _limitar(
            fator_horizontal_relativo,
            0.88,
            1.12,
        )
    )


    # ======================================================
    # COMPRIMENTO VISUAL DA ROUPA
    # ======================================================

    fator_vertical_relativo = (
        1.0
        + (
            fator_tronco
            - 1.0
        )
        * 0.40
    )

    fator_vertical_relativo = (
        _limitar(
            fator_vertical_relativo,
            0.94,
            1.06,
        )
    )


    classificacao = (
        _classificar_vestibilidade(
            fator_horizontal_relativo
        )
    )


    # ======================================================
    # PRODUTO
    # ======================================================

    tamanho = (
        tamanho_selecionado
        if tamanho_selecionado
        is not None
        else produto.get(
            "tamanho"
        )
    )


    # ======================================================
    # SAÍDA
    # ======================================================

    return {
        "versao": (
            "vestibilidade_avatar_v1"
        ),

        "status": (
            "vestibilidade_visual_calculada"
        ),

        "disponivel": True,

        "origem": (
            "avatar_builder"
        ),

        "perfil_avatar": {
            "genero": (
                genero
            ),

            "altura_aproximada_cm": (
                _arredondar(
                    altura_cm,
                    2,
                )
            ),

            "peso_aproximado_kg": (
                _arredondar(
                    peso_kg,
                    2,
                )
            ),

            "porte_corporal": (
                porte_corporal
            ),

            "proporcao_tronco": (
                proporcao_tronco
            ),

            "proporcao_pernas": (
                proporcao_pernas
            ),
        },

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
                produto.get(
                    "categoria"
                )
            ),

            "modelagem": (
                produto.get(
                    "modelagem"
                )
            ),

            "tamanho": (
                tamanho
            ),
        },

        "fatores_corpo": {
            "altura": (
                _arredondar(
                    fator_altura
                )
            ),

            "largura": (
                _arredondar(
                    fator_largura_corpo
                )
            ),

            "ombros": (
                _arredondar(
                    fator_ombros
                )
            ),

            "quadril": (
                _arredondar(
                    fator_quadril
                )
            ),

            "tronco": (
                _arredondar(
                    fator_tronco
                )
            ),

            "pernas": (
                _arredondar(
                    fator_pernas
                )
            ),
        },

        "vestibilidade_visual": {
            "classificacao": (
                classificacao
            ),

            "fator_horizontal_relativo": (
                _arredondar(
                    fator_horizontal_relativo
                )
            ),

            "fator_vertical_relativo": (
                _arredondar(
                    fator_vertical_relativo
                )
            ),

            "interpretacao": (
                "tendencia_visual"
            ),
        },

        "integracao_caimento_visual": {
            "multiplicador_horizontal_avatar": (
                _arredondar(
                    fator_horizontal_relativo
                )
            ),

            "multiplicador_vertical_avatar": (
                _arredondar(
                    fator_vertical_relativo
                )
            ),

            "pronto_para_integracao": True,
        },

        "capacidades": {
            "considera_avatar_builder": True,

            "considera_altura_aproximada": True,

            "considera_peso_aproximado": True,

            "considera_porte": True,

            "considera_tronco": True,

            "considera_pernas": True,

            "considera_genero_visual": True,

            "tamanho_recebido": (
                tamanho is not None
            ),
        },

        "restricoes": {
            "usa_medidas_reais_corpo": False,

            "calcula_circunferencia": False,

            "calcula_folga_cm": False,

            "simula_tecido": False,

            "simula_gravidade": False,

            "simula_colisao": False,

            "recomenda_tamanho": False,

            "representa_ajuste_fisico_exato": False,
        },

        "vestibilidade_calculada": True,

        "experimental": True,

        "mensagem": (
            "Vestibilidade visual do avatar "
            "calculada a partir do perfil "
            "aproximado configurado pelo usuário. "
            "O resultado representa tendência "
            "visual e não ajuste físico exato."
        ),
    }