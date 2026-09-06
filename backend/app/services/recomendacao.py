# ==========================================================
# VESTEIA — MOTOR DE RECOMENDAÇÃO
# ==========================================================
#
# Sprint — Grade Dinâmica de Tamanhos
#
# REGRA ARQUITETURAL:
#
# O VesteIA NÃO determina quais tamanhos uma loja utiliza.
#
# A grade deve vir do catálogo do comércio.
#
# Exemplos válidos:
#
# ["PP", "P", "M", "G", "GG", "EXG", "GG2"]
#
# ["34", "36", "38", "40", "42", "44", "46"]
#
# ["XS", "S", "M", "L", "XL", "2XL", "3XL"]
#
# ["Único"]
#
# O nome original do tamanho deve ser preservado.
# ==========================================================


# ==========================================================
# FALLBACK TEMPORÁRIO DO MVP
# ==========================================================
#
# Esta grade NÃO é uma regra do VesteIA.
#
# Ela existe somente para manter compatibilidade com
# os fluxos antigos do MVP enquanto o catálogo é migrado
# para fornecer sua própria grade dinamicamente.
#
# Depois da integração catálogo -> variantes,
# o fluxo principal não dependerá deste fallback.
# ==========================================================

GRADE_DEMONSTRATIVA_MVP = [
    "P",
    "M",
    "G",
    "GG",
]


def normalizar_grade_tamanhos(
    grade_tamanhos,
):
    """
    Normaliza uma grade recebida do catálogo.

    Aceita:

    [
        "PP",
        "P",
        "M",
        "G",
    ]

    ou:

    [
        {
            "tamanho": "PP",
        },
        {
            "tamanho": "P",
        },
    ]

    IMPORTANTE:

    - preserva o nome original do tamanho;
    - preserva a ordem enviada pela loja;
    - remove valores vazios;
    - remove duplicados;
    - não converte GG2 para 3XL;
    - não assume equivalência entre marcas.
    """

    if not grade_tamanhos:
        return []

    tamanhos_normalizados = []

    for item in grade_tamanhos:

        if isinstance(
            item,
            dict,
        ):
            tamanho = (
                item.get(
                    "tamanho"
                )
                or item.get(
                    "tamanho_original"
                )
                or item.get(
                    "size"
                )
            )

        else:
            tamanho = item

        if tamanho is None:
            continue

        tamanho = str(
            tamanho
        ).strip()

        if not tamanho:
            continue

        if (
            tamanho
            not in tamanhos_normalizados
        ):
            tamanhos_normalizados.append(
                tamanho
            )

    return tamanhos_normalizados


def _obter_grade(
    grade_tamanhos=None,
):
    """
    Retorna a grade utilizada pelo motor.

    Quando uma grade real é informada,
    utiliza exclusivamente a grade da loja.

    O fallback atual existe apenas
    para compatibilidade temporária
    com o catálogo demonstrativo do MVP.
    """

    grade = (
        normalizar_grade_tamanhos(
            grade_tamanhos
        )
    )

    if grade:
        return grade

    return list(
        GRADE_DEMONSTRATIVA_MVP
    )


def _buscar_indice_tamanho(
    tamanho_atual,
    grade_tamanhos,
):
    """
    Localiza um tamanho dentro da grade.

    A comparação prioriza igualdade exata.

    Como proteção para integrações externas,
    também aceita comparação sem diferença
    de maiúsculas/minúsculas.
    """

    if tamanho_atual is None:
        return None

    tamanho_texto = str(
        tamanho_atual
    ).strip()

    if not tamanho_texto:
        return None

    # Primeiro:
    # correspondência exata.

    for indice, tamanho in enumerate(
        grade_tamanhos
    ):
        if tamanho == tamanho_texto:
            return indice

    # Segundo:
    # correspondência tolerante
    # a maiúsculas/minúsculas.

    tamanho_comparacao = (
        tamanho_texto.lower()
    )

    for indice, tamanho in enumerate(
        grade_tamanhos
    ):
        if (
            str(tamanho)
            .strip()
            .lower()
            == tamanho_comparacao
        ):
            return indice

    return None


def mover_tamanho_na_grade(
    tamanho_atual,
    deslocamento,
    grade_tamanhos=None,
):
    """
    Move um tamanho dentro da grade
    fornecida pelo catálogo.

    Exemplos:

    grade:
    PP, P, M, G, GG, EXG

    P + 1 -> M
    GG + 1 -> EXG

    grade:
    34, 36, 38, 40, 42

    38 + 1 -> 40
    40 - 1 -> 38

    Nenhum nome de tamanho é fixado
    dentro desta função.
    """

    grade = (
        _obter_grade(
            grade_tamanhos
        )
    )

    if not grade:
        return tamanho_atual

    indice_atual = (
        _buscar_indice_tamanho(
            tamanho_atual,
            grade,
        )
    )

    if indice_atual is None:
        return tamanho_atual

    try:
        deslocamento = int(
            deslocamento
        )

    except (
        TypeError,
        ValueError,
    ):
        return tamanho_atual

    novo_indice = (
        indice_atual
        + deslocamento
    )

    # Protege o início da grade.

    if novo_indice < 0:
        novo_indice = 0

    # Protege o final da grade.

    if novo_indice >= len(
        grade
    ):
        novo_indice = (
            len(
                grade
            )
            - 1
        )

    return grade[
        novo_indice
    ]


def _aumentar_tamanho(
    tamanho_atual,
    grade_tamanhos=None,
):
    """
    Avança uma posição na grade
    daquele produto.

    Não existe mais dependência
    de P/M/G/GG.
    """

    return mover_tamanho_na_grade(
        tamanho_atual=tamanho_atual,
        deslocamento=1,
        grade_tamanhos=grade_tamanhos,
    )


def _diminuir_tamanho(
    tamanho_atual,
    grade_tamanhos=None,
):
    """
    Retrocede uma posição na grade
    daquele produto.

    Não existe mais dependência
    de P/M/G/GG.
    """

    return mover_tamanho_na_grade(
        tamanho_atual=tamanho_atual,
        deslocamento=-1,
        grade_tamanhos=grade_tamanhos,
    )


def _selecionar_tamanho_base_grade(
    altura_cm,
    peso_kg,
    grade_tamanhos=None,
):
    """
    Seleciona provisoriamente uma posição
    dentro da grade disponível.

    IMPORTANTE:

    Esta função mantém o comportamento
    demonstrativo antigo do MVP.

    Ela NÃO representa ainda o futuro
    motor dimensional definitivo do VesteIA.

    O objetivo desta etapa é:

    - remover nomes fixos de tamanho;
    - permitir qualquer grade;
    - manter o MVP atual funcionando.

    Futuramente a posição será escolhida
    pelas medidas reais das variantes
    disponibilizadas pela loja.
    """

    grade = (
        _obter_grade(
            grade_tamanhos
        )
    )

    if not grade:
        return None

    quantidade = len(
        grade
    )

    if quantidade == 1:
        return grade[0]

    # ======================================================
    # CLASSIFICAÇÃO PROVISÓRIA DO MVP
    # ======================================================
    #
    # Antes:
    #
    # condição 1 -> P
    # condição 2 -> M
    # condição 3 -> G
    # condição 4 -> GG
    #
    # Agora:
    #
    # condição 1 -> início da grade
    # condição 2 -> aproximadamente 1/3
    # condição 3 -> aproximadamente 2/3
    # condição 4 -> final da grade
    #
    # Portanto funciona também com:
    #
    # 34, 36, 38, 40, 42, 44, 46
    #
    # ou:
    #
    # PP, P, M, G, GG, EXG, GG2
    #
    # sem conhecer os nomes.
    # ======================================================

    if (
        altura_cm < 160
        and peso_kg < 60
    ):
        percentual_grade = 0.0

    elif (
        altura_cm < 170
        and peso_kg < 70
    ):
        percentual_grade = 0.33

    elif (
        altura_cm < 180
        and peso_kg < 80
    ):
        percentual_grade = 0.66

    else:
        percentual_grade = 1.0

    indice = round(
        percentual_grade
        * (
            quantidade - 1
        )
    )

    indice = max(
        0,
        min(
            indice,
            quantidade - 1,
        ),
    )

    return grade[
        indice
    ]


def recomendar_tamanho(
    altura_cm: float,
    peso_kg: float,
    cintura_cm: float | None = None,
    preferencia_caimento: str | None = None,
    grade_tamanhos=None,
):
    """
    Calcula uma sugestão inicial de tamanho
    dentro da grade disponível do produto.

    A grade pode ser qualquer sequência
    fornecida pela loja.

    Exemplos:

    [
        "PP",
        "P",
        "M",
        "G",
        "GG",
        "EXG",
    ]

    [
        "34",
        "36",
        "38",
        "40",
        "42",
        "44",
    ]

    [
        "XS",
        "S",
        "M",
        "L",
        "XL",
        "2XL",
    ]

    IMPORTANTE:

    As regras de altura/peso continuam
    provisórias nesta etapa do MVP.

    Posteriormente serão substituídas
    pela comparação das medidas reais
    das variantes importadas da loja.
    """

    tamanho_base = (
        _selecionar_tamanho_base_grade(
            altura_cm=altura_cm,
            peso_kg=peso_kg,
            grade_tamanhos=grade_tamanhos,
        )
    )

    if tamanho_base is None:
        return None

    # A cintura pode solicitar
    # a próxima variante disponível.

    if (
        cintura_cm is not None
        and cintura_cm >= 100
    ):
        tamanho_base = (
            _aumentar_tamanho(
                tamanho_atual=tamanho_base,
                grade_tamanhos=grade_tamanhos,
            )
        )

    # Preferência de caimento:
    # também passa a navegar
    # pela grade real do produto.

    if preferencia_caimento is not None:

        preferencia_normalizada = (
            preferencia_caimento
            .strip()
            .lower()
        )

        if (
            preferencia_normalizada
            == "solto"
        ):
            tamanho_base = (
                _aumentar_tamanho(
                    tamanho_atual=tamanho_base,
                    grade_tamanhos=grade_tamanhos,
                )
            )

        elif (
            preferencia_normalizada
            == "justo"
        ):
            tamanho_base = (
                _diminuir_tamanho(
                    tamanho_atual=tamanho_base,
                    grade_tamanhos=grade_tamanhos,
                )
            )

    return tamanho_base


def explicar_recomendacao(
    tamanho_recomendado: str | None,
    cintura_cm: float | None = None,
    preferencia_caimento: str | None = None,
    grade_tamanhos=None,
):
    """
    Explica os principais fatores
    que influenciaram a sugestão.

    A grade é registrada somente
    para transparência do motor.
    """

    motivos = []

    if (
        cintura_cm is not None
        and cintura_cm >= 100
    ):
        motivos.append(
            (
                "a medida da cintura "
                "influenciou a posição "
                "selecionada na grade"
            )
        )

    if preferencia_caimento is not None:

        preferencia_normalizada = (
            preferencia_caimento
            .strip()
            .lower()
        )

        if (
            preferencia_normalizada
            == "solto"
        ):
            motivos.append(
                (
                    "preferência por caimento "
                    "solto avançou uma variante "
                    "na grade disponível"
                )
            )

        elif (
            preferencia_normalizada
            == "justo"
        ):
            motivos.append(
                (
                    "preferência por caimento "
                    "justo retrocedeu uma variante "
                    "na grade disponível"
                )
            )

    if not motivos:
        motivos.append(
            (
                "sugestão experimental baseada "
                "nos dados disponíveis"
            )
        )

    return {
        "tamanho_recomendado": (
            tamanho_recomendado
        ),

        "grade_tamanhos": (
            normalizar_grade_tamanhos(
                grade_tamanhos
            )
        ),

        "motivos": motivos,

        "grade_dinamica": True,

        "tamanho_padrao_vesteia": False,
    }


def calcular_confianca_recomendacao(
    altura_cm: float | None = None,
    peso_kg: float | None = None,
    cintura_cm: float | None = None,
):
    """
    Define o nível experimental
    de confiança da sugestão atual.

    Esta função não transforma
    a sugestão em recomendação
    dimensional definitiva.
    """

    if (
        altura_cm is not None
        and peso_kg is not None
        and cintura_cm is not None
    ):
        return "alta"

    if (
        altura_cm is not None
        and peso_kg is not None
    ):
        return "media"

    return None


def verificar_compatibilidade_peca(
    tamanho_recomendado: str | None,
    largura_cm: float | None = None,
    comprimento_cm: float | None = None,
    modelagem: str | None = None,
):
    """
    Analisa características cadastradas
    da peça.

    O nome do tamanho é tratado apenas
    como identificador da variante.

    Esta função não assume que:
    P < M < G < GG

    nem qualquer outra grade universal.
    """

    if modelagem is None:
        modelagem = "regular"

    modelagem_normalizada = (
        modelagem
        .strip()
        .lower()
    )

    observacoes = []

    if (
        modelagem_normalizada
        == "slim"
    ):
        observacoes.append(
            "modelagem ajustada"
        )

    elif (
        modelagem_normalizada
        == "oversized"
    ):
        observacoes.append(
            "modelagem ampla"
        )

    # ======================================================
    # OBSERVAÇÕES PROVISÓRIAS DO MVP
    # ======================================================
    #
    # Estes limites ainda não representam
    # compatibilidade dimensional definitiva.
    # ======================================================

    if (
        largura_cm is not None
        and largura_cm < 50
    ):
        observacoes.append(
            "largura menor que 50 cm"
        )

    if (
        comprimento_cm is not None
        and comprimento_cm < 65
    ):
        observacoes.append(
            "comprimento menor que 65 cm"
        )

    if not observacoes:
        observacoes.append(
            "caimento compatível"
        )

    return {
        "tamanho": (
            tamanho_recomendado
        ),

        "largura_cm": (
            largura_cm
        ),

        "comprimento_cm": (
            comprimento_cm
        ),

        "modelagem": (
            modelagem
        ),

        "observacoes": (
            observacoes
        ),

        "grade_dinamica": True,
    }