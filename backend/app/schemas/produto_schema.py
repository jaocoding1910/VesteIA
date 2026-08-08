from pydantic import BaseModel

class ProdutoSchema(BaseModel):
    nome: str
    preco: float
    tamanho: str
    cor: str
    categoria: str