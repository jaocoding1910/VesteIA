import unicodedata


# ==========================================================
# FAMÍLIAS DE VESTIMENTA
# ==========================================================
#
# A categoria identifica o tipo comercial da peça.
#
# A família identifica como essa peça se relaciona
# estruturalmente com o corpo e com o renderer.
#
# Exemplos:
#
# camiseta -> superior
# calça -> inferior
# vestido -> corpo_integrado
# tênis -> calcado
#
# Isso permite adicionar novas categorias no futuro
# sem reescrever todo o pipeline.
# ==========================================================

FAMILIA_SUPERIOR = "superior"
FAMILIA_INFERIOR = "inferior"
FAMILIA_CORPO_INTEGRADO = "corpo_integrado"
FAMILIA_CALCADO = "calcado"


# ==========================================================
# CATEGORIAS OFICIAIS DO MVP
# ==========================================================

CATEGORIAS_VESTUARIO = {

    # ------------------------------------------------------
    # SUPERIORES
    # ------------------------------------------------------

    "camiseta": {
        "familia": FAMILIA_SUPERIOR,
        "regiao_prioritaria": "tronco",
        "renderer": "camiseta",
        "disponivel_mvp": True,
    },

    "camisa": {
        "familia": FAMILIA_SUPERIOR,
        "regiao_prioritaria": "tronco",
        "renderer": "camisa",
        "disponivel_mvp": True,
    },

    "regata": {
        "familia": FAMILIA_SUPERIOR,
        "regiao_prioritaria": "tronco",
        "renderer": "regata",
        "disponivel_mvp": True,
    },

    "jaqueta": {
        "familia": FAMILIA_SUPERIOR,
        "regiao_prioritaria": "tronco",
        "renderer": "jaqueta",
        "disponivel_mvp": True,
    },

    "casaco": {
        "familia": FAMILIA_SUPERIOR,
        "regiao_prioritaria": "tronco",
        "renderer": "casaco",
        "disponivel_mvp": True,
    },

    # ------------------------------------------------------
    # INFERIORES
    # ------------------------------------------------------

    "calca": {
        "familia": FAMILIA_INFERIOR,
        "regiao_prioritaria": "quadril_pernas",
        "renderer": "calca",
        "disponivel_mvp": True,
    },

    "short": {
        "familia": FAMILIA_INFERIOR,
        "regiao_prioritaria": "quadril_pernas",
        "renderer": "short",
        "disponivel_mvp": True,
    },

    "bermuda": {
        "familia": FAMILIA_INFERIOR,
        "regiao_prioritaria": "quadril_pernas",
        "renderer": "bermuda",
        "disponivel_mvp": True,
    },

    "saia": {
        "familia": FAMILIA_INFERIOR,
        "regiao_prioritaria": "quadril_pernas",
        "renderer": "saia",
        "disponivel_mvp": True,
    },

    # ------------------------------------------------------
    # CORPO INTEGRADO
    # ------------------------------------------------------

    "vestido": {
        "familia": FAMILIA_CORPO_INTEGRADO,
        "regiao_prioritaria": "corpo_integrado",
        "renderer": "vestido",
        "disponivel_mvp": True,
    },

    "macacao": {
        "familia": FAMILIA_CORPO_INTEGRADO,
        "regiao_prioritaria": "corpo_integrado",
        "renderer": "macacao",
        "disponivel_mvp": True,
    },

    # ------------------------------------------------------
    # CALÇADOS
    # ------------------------------------------------------

    "tenis": {
        "familia": FAMILIA_CALCADO,
        "regiao_prioritaria": "pes",
        "renderer": "tenis",
        "disponivel_mvp": True,
    },

    "sapato": {
        "familia": FAMILIA_CALCADO,
        "regiao_prioritaria": "pes",
        "renderer": "sapato",
        "disponivel_mvp": True,
    },

    "bota": {
        "familia": FAMILIA_CALCADO,
        "regiao_prioritaria": "pes",
        "renderer": "bota",
        "disponivel_mvp": True,
    },

    "calcado": {
        "familia": FAMILIA_CALCADO,
        "regiao_prioritaria": "pes",
        "renderer": "calcado",
        "disponivel_mvp": True,
    },
}


# ==========================================================
# ALIASES
# ==========================================================
#
# Permite receber categorias vindas de:
#
# - banco atual;
# - frontend;
# - APIs externas;
# - catálogos de e-commerce;
# - singular/plural;
# - português com ou sem acento.
#
# O pipeline trabalhará internamente somente
# com as categorias oficiais acima.
# ==========================================================

ALIASES_CATEGORIAS = {

    # CAMISETA
    "camiseta": "camiseta",
    "camisetas": "camiseta",
    "t-shirt": "camiseta",
    "tshirt": "camiseta",
    "t shirt": "camiseta",

    # CAMISA
    "camisa": "camisa",
    "camisas": "camisa",

    # REGATA
    "regata": "regata",
    "regatas": "regata",

    # JAQUETA
    "jaqueta": "jaqueta",
    "jaquetas": "jaqueta",

    # CASACO
    "casaco": "casaco",
    "casacos": "casaco",

    # CALÇA
    "calca": "calca",
    "calcas": "calca",
    "calça": "calca",
    "calças": "calca",
    "calca jeans": "calca",
    "calça jeans": "calca",
    "jeans": "calca",

    # SHORT
    "short": "short",
    "shorts": "short",

    # BERMUDA
    "bermuda": "bermuda",
    "bermudas": "bermuda",

    # SAIA
    "saia": "saia",
    "saias": "saia",

    # VESTIDO
    "vestido": "vestido",
    "vestidos": "vestido",

    # MACACÃO
    "macacao": "macacao",
    "macacoes": "macacao",
    "macacão": "macacao",
    "macacões": "macacao",

    # TÊNIS
    "tenis": "tenis",
    "tênis": "tenis",

    # SAPATO
    "sapato": "sapato",
    "sapatos": "sapato",

    # BOTA
    "bota": "bota",
    "botas": "bota",

    # CALÇADO GENÉRICO
    "calcado": "calcado",
    "calcados": "calcado",
    "calçado": "calcado",
    "calçados": "calcado",
}


def _remover_acentos(
    texto,
):
    """
    Remove acentos sem alterar
    outros caracteres do texto.
    """

    if not isinstance(
        texto,
        str,
    ):
        return ""

    normalizado = unicodedata.normalize(
        "NFD",
        texto,
    )

    return "".join(
        caractere
        for caractere in normalizado
        if unicodedata.category(
            caractere
        )
        != "Mn"
    )


def normalizar_categoria(
    categoria,
):
    """
    Converte uma categoria externa
    para a categoria oficial interna
    do VesteIA.

    Retorna None quando não reconhecida.
    """

    if categoria is None:
        return None

    texto = str(
        categoria
    ).strip().lower()

    if not texto:
        return None

    # Primeiro tentamos exatamente como recebido.
    categoria_oficial = (
        ALIASES_CATEGORIAS.get(
            texto
        )
    )

    if categoria_oficial:
        return categoria_oficial

    # Depois tentamos sem acentos.
    texto_sem_acentos = (
        _remover_acentos(
            texto
        )
    )

    categoria_oficial = (
        ALIASES_CATEGORIAS.get(
            texto_sem_acentos
        )
    )

    if categoria_oficial:
        return categoria_oficial

    return None


def obter_configuracao_categoria(
    categoria,
):
    """
    Retorna a configuração estrutural
    da categoria.
    """

    categoria_normalizada = (
        normalizar_categoria(
            categoria
        )
    )

    if categoria_normalizada is None:
        return None

    configuracao = (
        CATEGORIAS_VESTUARIO.get(
            categoria_normalizada
        )
    )

    if configuracao is None:
        return None

    return {
        "categoria": (
            categoria_normalizada
        ),
        **configuracao,
    }


def obter_familia_categoria(
    categoria,
):
    """
    Retorna somente a família
    estrutural da categoria.
    """

    configuracao = (
        obter_configuracao_categoria(
            categoria
        )
    )

    if configuracao is None:
        return None

    return configuracao.get(
        "familia"
    )


def obter_regiao_prioritaria(
    categoria,
):
    """
    Retorna a região corporal
    prioritária da categoria.
    """

    configuracao = (
        obter_configuracao_categoria(
            categoria
        )
    )

    if configuracao is None:
        return None

    return configuracao.get(
        "regiao_prioritaria"
    )


def obter_renderer_categoria(
    categoria,
):
    """
    Retorna o renderer previsto
    para a categoria.
    """

    configuracao = (
        obter_configuracao_categoria(
            categoria
        )
    )

    if configuracao is None:
        return None

    return configuracao.get(
        "renderer"
    )


def categoria_disponivel_mvp(
    categoria,
):
    """
    Informa se a categoria faz parte
    do catálogo funcional previsto
    para o MVP multivestimenta.
    """

    configuracao = (
        obter_configuracao_categoria(
            categoria
        )
    )

    if configuracao is None:
        return False

    return bool(
        configuracao.get(
            "disponivel_mvp",
            False,
        )
    )


def listar_categorias_mvp():
    """
    Lista as categorias oficiais
    disponíveis no MVP.
    """

    return [
        categoria
        for (
            categoria,
            configuracao,
        ) in CATEGORIAS_VESTUARIO.items()
        if configuracao.get(
            "disponivel_mvp",
            False,
        )
    ]