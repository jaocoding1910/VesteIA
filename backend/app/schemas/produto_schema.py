from pydantic import BaseModel


class ProdutoSchema(BaseModel):
    """
    Define os dados necessários para representar um produto.

    É utilizado principalmente para validar os dados recebidos
    pela API nas operações de criação e atualização.
    """

    nome: str
    preco: float
    tamanho: str
    cor: str
    categoria: str

    # Informações físicas da peça usadas pelo motor de recomendação.
    largura_cm: float | None = None
    comprimento_cm: float | None = None
    modelagem: str | None = None


class ProdutoResponse(ProdutoSchema):
    """
    Define os dados devolvidos pela API.

    Herda todos os campos de ProdutoSchema e acrescenta
    o ID gerado pelo PostgreSQL.
    """

    id: int