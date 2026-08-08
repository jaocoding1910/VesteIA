from fastapi import APIRouter, HTTPException
from app.schemas.produto_schema import ProdutoSchema
from app.models.produto import Produto
from app.services.catalogo import (buscar_produto_por_categoria, buscar_produto_por_id, listar_produtos, adicionar_produto, atualizar_produto, deletar_produto, buscar_produto_por_categoria_tamanho_cor)


router = APIRouter()

@router.get("/")
def inicio(nome: str = "Visitante"):
    return {"mensagem": f"Bem-vindo ao VesteIA, {nome}!"}


@router.get("/sobre")
def sobre():
    return {"mensagem": "VesteIA é uma plataforma de recomendação de roupas baseada em IA."}


@router.get("/produtos", response_model=list[ProdutoSchema])
def produtos():
    return listar_produtos()


@router.post("/produtos", response_model=ProdutoSchema)
def criar_produto(produto: ProdutoSchema):
    novo_produto = Produto(
        nome=produto.nome,
        preco=produto.preco,
        tamanho=produto.tamanho,
        cor=produto.cor,
        categoria=produto.categoria
    )
    adicionar_produto(novo_produto)

    return novo_produto


@router.put("/produtos/{id}", response_model=ProdutoSchema)
def editar_produto(id: int, produto: ProdutoSchema):

    produto_existente = buscar_produto_por_id(id)

    if produto_existente is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return atualizar_produto(id, produto)


@router.delete("/produtos/{id}")
def excluir_produto(id: int):
    produto = buscar_produto_por_id(id)

    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    deletar_produto(id)
    return {"mensagem": "Produto excluído com sucesso"}

# FILTRO
@router.get("/produtos/filtro",response_model=list[ProdutoSchema])
def buscar_produtos_por_categoria_tamanho_cor(

    categoria: str | None = None,
    tamanho: str | None = None,
    cor: str | None = None
    ):

    return buscar_produto_por_categoria_tamanho_cor(
        categoria,
        tamanho,
        cor
    )


# BUSCAR POR ID
@router.get("/produtos/{id}", response_model=ProdutoSchema)
def buscar_produto(id: int):
    produto = buscar_produto_por_id(id)

    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto
