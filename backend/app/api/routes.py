from fastapi import APIRouter, HTTPException

from app.models.produto import Produto
from app.perfil import perfil_usuario
from app.schemas.produto_schema import ProdutoResponse, ProdutoSchema
from app.services.catalogo import (
    adicionar_produto,
    atualizar_produto,
    buscar_produto_por_categoria_tamanho_cor,
    buscar_produto_por_id,
    deletar_produto,
    listar_produtos,
)
from app.services.recomendacao import (
    calcular_confianca_recomendacao,
    explicar_recomendacao,
    recomendar_tamanho,
    verificar_compatibilidade_peca,
)


# Agrupa todas as rotas HTTP do backend do VesteIA.
router = APIRouter()


# ==========================================================
# ROTAS INSTITUCIONAIS
# ==========================================================

@router.get("/")
def inicio(nome: str = "Visitante"):
    """Retorna a mensagem inicial da API."""
    return {
        "mensagem": f"Bem-vindo ao VesteIA, {nome}!"
    }


@router.get("/sobre")
def sobre():
    """Retorna uma descrição resumida do projeto."""
    return {
        "mensagem": (
            "VesteIA é uma plataforma de recomendação "
            "de roupas baseada em IA."
        )
    }


# ==========================================================
# CRUD DE PRODUTOS
# ==========================================================

@router.get("/produtos", response_model=list[ProdutoResponse])
def produtos():
    """Lista todos os produtos cadastrados no PostgreSQL."""
    return listar_produtos()


@router.post("/produtos", response_model=ProdutoResponse)
def criar_produto(produto: ProdutoSchema):
    """Cria um produto e retorna também o ID gerado pelo banco."""

    novo_produto = Produto(
        nome=produto.nome,
        preco=produto.preco,
        tamanho=produto.tamanho,
        cor=produto.cor,
        categoria=produto.categoria,
        largura_cm=produto.largura_cm,
        comprimento_cm=produto.comprimento_cm,
        modelagem=produto.modelagem,
    )

    return adicionar_produto(novo_produto)


@router.put("/produtos/{id}", response_model=ProdutoResponse)
def editar_produto(id: int, produto: ProdutoSchema):
    """Atualiza completamente um produto existente."""

    produto_existente = buscar_produto_por_id(id)

    if produto_existente is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    return atualizar_produto(id, produto)


@router.delete("/produtos/{id}")
def excluir_produto(id: int):
    """Exclui um produto pelo ID."""

    produto = buscar_produto_por_id(id)

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    deletar_produto(id)

    return {
        "mensagem": "Produto excluído com sucesso"
    }


# ==========================================================
# FILTROS E CONSULTAS DE PRODUTOS
# ==========================================================

@router.get("/produtos/filtro", response_model=list[ProdutoResponse])
def buscar_produtos_por_categoria_tamanho_cor(
    categoria: str | None = None,
    tamanho: str | None = None,
    cor: str | None = None,
    largura_cm: float | None = None,
    comprimento_cm: float | None = None,
    modelagem: str | None = None,
):
    """
    Busca produtos utilizando somente os filtros informados.
    """

    return buscar_produto_por_categoria_tamanho_cor(
        categoria,
        tamanho,
        cor,
        largura_cm,
        comprimento_cm,
        modelagem,
    )


@router.get("/produtos/{id}", response_model=ProdutoResponse)
def buscar_produto(id: int):
    """Busca um único produto pelo ID."""

    produto = buscar_produto_por_id(id)

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    return produto


# ==========================================================
# MOTOR DE RECOMENDAÇÃO
# ==========================================================

@router.get("/recomendar-tamanho")
def recomendar_tamanho_endpoint(
    altura_cm: float,
    peso_kg: float,
    cintura_cm: float | None = None,
    preferencia_caimento: str | None = None,
):
    """
    Calcula o tamanho recomendado para o usuário
    e explica os principais motivos da recomendação.
    """

    tamanho_recomendado = recomendar_tamanho(
        altura_cm,
        peso_kg,
        cintura_cm,
        preferencia_caimento,
    )

    explicacao = explicar_recomendacao(
        tamanho_recomendado,
        cintura_cm,
        preferencia_caimento,
    )

    return {
        "tamanho_recomendado": tamanho_recomendado,
        "motivos": explicacao["motivos"],
    }


@router.get("/recomendar-produtos")
def recomendar_produtos(
    altura_cm: float | None = None,
    peso_kg: float | None = None,
    cintura_cm: float | None = None,
    categoria: str | None = None,
    modelagem: str | None = None,
    preferencia_caimento: str | None = None,
):
    """
    Recomenda um tamanho e busca produtos compatíveis
    com o perfil e os filtros informados.
    """

    # Se altura e peso não vierem na requisição,
    # tenta utilizar os dados armazenados no perfil.
    if altura_cm is None and peso_kg is None:
        altura_cm = perfil_usuario["altura_cm"]
        peso_kg = perfil_usuario["peso_kg"]

        if cintura_cm is None:
            cintura_cm = perfil_usuario["cintura_cm"]

    # Para recomendar tamanho, altura e peso devem existir juntos.
    if (altura_cm is None) != (peso_kg is None):
        raise HTTPException(
            status_code=400,
            detail=(
                "Para recomendar o tamanho, "
                "informe altura e peso juntos."
            ),
        )

    # Calcula o tamanho, a explicação e a confiança da recomendação.
    if altura_cm is not None and peso_kg is not None:
        tamanho_recomendado = recomendar_tamanho(
            altura_cm,
            peso_kg,
            cintura_cm,
            preferencia_caimento,
        )

        explicacao = explicar_recomendacao(
            tamanho_recomendado,
            cintura_cm,
            preferencia_caimento,
        )

        confianca = calcular_confianca_recomendacao(
        altura_cm,
        peso_kg,
        cintura_cm,
    )

    else:
        tamanho_recomendado = None
        explicacao = None

    # Define a mensagem de acordo com o estado do perfil.
    if tamanho_recomendado is not None:
        mensagem = (
            "Encontramos produtos compatíveis com o seu perfil."
        )
    else:
        mensagem = (
            "Perfil sem altura e peso cadastrados. "
            "Confira os produtos disponíveis."
        )

    # Consulta o catálogo utilizando apenas os filtros disponíveis.
    produtos = buscar_produto_por_categoria_tamanho_cor(
        categoria=categoria,
        tamanho=tamanho_recomendado,
        cor=None,
        largura_cm=None,
        comprimento_cm=None,
        modelagem=modelagem,
    )

    # Não encontrar estoque não significa que a recomendação falhou.
    if not produtos:
        if tamanho_recomendado is not None:
            mensagem = (
                f"Seu tamanho recomendado é {tamanho_recomendado}, "
                "mas não encontramos produtos disponíveis nesse tamanho."
            )
        else:
            mensagem = (
                "Nenhum produto foi encontrado para os filtros informados."
            )

        return {
            "mensagem": mensagem,
            "tamanho_recomendado": tamanho_recomendado,
            "confianca": confianca,
            "explicacao": explicacao,
            "produtos": [],
        }

    # Analisa individualmente as características de cada peça encontrada.
    for produto in produtos:
        analise = verificar_compatibilidade_peca(
            tamanho_recomendado=produto["tamanho"],
            largura_cm=produto["largura_cm"],
            comprimento_cm=produto["comprimento_cm"],
            modelagem=produto["modelagem"],
        )

        produto["observacoes"] = analise["observacoes"]

    return {
        "mensagem": mensagem,
        "tamanho_recomendado": tamanho_recomendado,
        "confianca": confianca,
        "explicacao": explicacao,
        "produtos": produtos,
    }


# ==========================================================
# PERFIL CORPORAL
# ==========================================================

@router.get("/perfil")
def obter_perfil():
    """Retorna o perfil corporal atualmente armazenado."""
    return perfil_usuario


@router.put("/perfil")
def atualizar_perfil(
    altura_cm: float | None = None,
    peso_kg: float | None = None,
    cintura_cm: float | None = None,
):
    """Atualiza os dados corporais utilizados na recomendação."""

    perfil_usuario["altura_cm"] = altura_cm
    perfil_usuario["peso_kg"] = peso_kg
    perfil_usuario["cintura_cm"] = cintura_cm

    return {
        "mensagem": "Perfil atualizado com sucesso",
        "perfil": perfil_usuario,
    }