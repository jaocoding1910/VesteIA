class Produto:
    """
    Representa um produto dentro da aplicação VesteIA.

    Esta classe organiza os dados do produto antes que eles
    sejam enviados para as operações do catálogo/PostgreSQL.
    """

    def __init__(
        self,
        nome: str,
        preco: float,
        tamanho: str,
        cor: str,
        categoria: str,
        largura_cm: float | None = None,
        comprimento_cm: float | None = None,
        modelagem: str | None = None,
    ):
        self.nome = nome
        self.preco = preco
        self.tamanho = tamanho
        self.cor = cor
        self.categoria = categoria
        self.largura_cm = largura_cm
        self.comprimento_cm = comprimento_cm
        self.modelagem = modelagem