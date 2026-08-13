from pydantic import BaseModel

class ProdutoSchema(BaseModel):
    nome: str
    preco: float
    tamanho: str
    cor: str
    categoria: str
    largura_cm: float | None = None
    comprimento_cm: float | None = None
    modelagem: str | None = None


class ProdutoResponse(ProdutoSchema):
    id: int
