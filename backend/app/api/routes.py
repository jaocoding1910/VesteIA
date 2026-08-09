import os

from fastapi import APIRouter, HTTPException
from app.schemas.produto_schema import ProdutoSchema
from app.models.produto import Produto
from app.services.catalogo import (buscar_produto_por_categoria, buscar_produto_por_id, listar_produtos, adicionar_produto, atualizar_produto, deletar_produto, buscar_produto_por_categoria_tamanho_cor)
from app.services.recomendacao import recomendar_tamanho
from app.perfil import perfil_usuario

router = APIRouter()

@router.get("/")
def inicio(nome: str = "Visitante"):
    return {
        "mensagem": f"Bem-vindo ao VesteIA, {nome}!"}


@router.get("/sobre")
def sobre():
    return {
        "mensagem": "VesteIA é uma plataforma de recomendação de roupas baseada em IA."}


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
    return {
        "mensagem": "Produto excluído com sucesso"}

# FILTRO
@router.get("/produtos/filtro",response_model=list[ProdutoSchema])
def buscar_produtos_por_categoria_tamanho_cor(

    categoria: str | None = None,
    tamanho: str | None = None,
    cor: str | None = None,
    largura_cm: float | None = None,
    comprimento_cm: float | None = None
    ):

    return buscar_produto_por_categoria_tamanho_cor(
        categoria,
        tamanho,
        cor,
        largura_cm,
        comprimento_cm
    )


# BUSCAR POR ID
@router.get("/produtos/{id}", response_model=ProdutoSchema)
def buscar_produto(id: int):
    produto = buscar_produto_por_id(id)

    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto


@router.get("/recomendar-tamanho")
def recomendar_tamanho_endpoint(altura_cm: float, peso_kg: float):
    tamanho_recomendado = recomendar_tamanho(altura_cm, peso_kg)
    return {
        "tamanho_recomendado": tamanho_recomendado}


@router.get("/recomendar-produtos")
def recomendar_produtos(
    altura_cm: float | None = None,
    peso_kg: float | None = None,
    categoria: str | None = None,
    modelagem: str | None = None
):

    if altura_cm is None and peso_kg is None:
        altura_cm = perfil_usuario["altura_cm"]
        peso_kg = perfil_usuario["peso_kg"]

    if (altura_cm is None) != (peso_kg is None):
        raise HTTPException(
            status_code=400,
            detail="Para recomendar o tamanho, informe altura e peso juntos."
        )

    if altura_cm is not None and peso_kg is not None:
        tamanho_recomendado = recomendar_tamanho(altura_cm, peso_kg)
    else:
        tamanho_recomendado = None

    if tamanho_recomendado is not None:
        mensagem = "Encontramos produtos compatíveis com o seu perfil."

    elif altura_cm is None and peso_kg is None:
        mensagem = "Perfil sem altura e peso cadastrados. Confira os produtos disponíveis."

    else:
        mensagem = "Confira os produtos disponíveis."

    produtos = buscar_produto_por_categoria_tamanho_cor(
        categoria=categoria,
        tamanho=tamanho_recomendado,
        cor=None,
        largura_cm=None,
        comprimento_cm=None,
        modelagem=modelagem
    )

    if not produtos:
        raise HTTPException(
            status_code=404,
            detail="Nenhum produto encontrado para os filtros informados."
        )

    return {
        "mensagem": mensagem,
        "tamanho_recomendado": tamanho_recomendado,
        "produtos": produtos
    }


@router.get("/perfil")
def obter_perfil():
    return perfil_usuario


@router.put("/perfil")
def atualizar_perfil(
    altura_cm: float | None = None,
    peso_kg: float | None = None):

    perfil_usuario["altura_cm"] = altura_cm
    perfil_usuario["peso_kg"] = peso_kg

    return {
        "mensagem": "Perfil atualizado com sucesso", "perfil": perfil_usuario}