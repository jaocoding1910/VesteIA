from fastapi import APIRouter, HTTPException

from app.models.produto import Produto
from app.perfil import perfil_usuario
from app.schemas.produto_schema import (
    ProdutoResponse,
    ProdutoSchema,
)
from app.services.catalogo import (
    adicionar_produto,
    atualizar_produto,
    buscar_produto_por_categoria_tamanho_cor,
    buscar_produto_por_id,
    deletar_produto,
    listar_produtos,
    obter_grade_tamanhos_produto,
    obter_variantes_produto,
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
# UTILITÁRIOS INTERNOS
# ==========================================================

def _normalizar_texto(valor):
    """
    Normaliza texto apenas para comparações internas.

    O valor original continua sendo preservado
    nas respostas e no catálogo.
    """

    if valor is None:
        return ""

    return str(
        valor
    ).strip().lower()


def _chave_modelo_produto(
    produto: dict,
):
    """
    Identifica um mesmo modelo comercial.

    Nesta fase do MVP consideramos variantes
    do mesmo produto os registros com:

    - mesmo nome;
    - mesma cor;
    - mesma categoria;
    - mesma modelagem.

    O tamanho pode variar livremente.
    """

    return (
        _normalizar_texto(
            produto.get("nome")
        ),
        _normalizar_texto(
            produto.get("cor")
        ),
        _normalizar_texto(
            produto.get("categoria")
        ),
        _normalizar_texto(
            produto.get("modelagem")
        ),
    )


def _agrupar_produtos_por_modelo(
    produtos,
):
    """
    Agrupa registros de variantes por modelo
    sem assumir nenhuma grade universal.
    """

    grupos = {}

    for produto in produtos:

        chave = (
            _chave_modelo_produto(
                produto
            )
        )

        if chave not in grupos:
            grupos[chave] = []

        grupos[chave].append(
            produto
        )

    return list(
        grupos.values()
    )


def _buscar_variante_por_tamanho(
    variantes,
    tamanho,
):
    """
    Busca a variante que possui o tamanho
    selecionado pelo motor.

    A comparação é tolerante apenas a
    maiúsculas/minúsculas.

    Não converte, por exemplo:
    GG2 -> 3XL.
    """

    if tamanho is None:
        return None

    tamanho_comparacao = (
        _normalizar_texto(
            tamanho
        )
    )

    for variante in variantes:

        if (
            _normalizar_texto(
                variante.get(
                    "tamanho"
                )
            )
            == tamanho_comparacao
        ):
            return variante

    return None


# ==========================================================
# ROTAS INSTITUCIONAIS
# ==========================================================

@router.get("/")
def inicio(
    nome: str = "Visitante",
):
    """Retorna a mensagem inicial da API."""

    return {
        "mensagem": (
            f"Bem-vindo ao VesteIA, {nome}!"
        )
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

@router.get(
    "/produtos",
    response_model=list[ProdutoResponse],
)
def produtos():
    """
    Lista todos os produtos cadastrados
    no PostgreSQL.
    """

    return listar_produtos()


@router.post(
    "/produtos",
    response_model=ProdutoResponse,
)
def criar_produto(
    produto: ProdutoSchema,
):
    """
    Cria um produto e retorna também
    o ID gerado pelo banco.

    O campo tamanho é preservado exatamente
    como informado pelo catálogo.

    Exemplos válidos:
    PP, EXG, GG2, 34, 36, 44, 3XL etc.
    """

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

    return adicionar_produto(
        novo_produto
    )


@router.put(
    "/produtos/{id}",
    response_model=ProdutoResponse,
)
def editar_produto(
    id: int,
    produto: ProdutoSchema,
):
    """Atualiza completamente um produto existente."""

    produto_existente = (
        buscar_produto_por_id(
            id
        )
    )

    if produto_existente is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    return atualizar_produto(
        id,
        produto,
    )


@router.delete("/produtos/{id}")
def excluir_produto(
    id: int,
):
    """Exclui um produto pelo ID."""

    produto = buscar_produto_por_id(
        id
    )

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    deletar_produto(
        id
    )

    return {
        "mensagem": (
            "Produto excluído com sucesso"
        )
    }


# ==========================================================
# FILTROS E CONSULTAS DE PRODUTOS
# ==========================================================

@router.get(
    "/produtos/filtro",
    response_model=list[ProdutoResponse],
)
def buscar_produtos_por_categoria_tamanho_cor(
    categoria: str | None = None,
    tamanho: str | None = None,
    cor: str | None = None,
    largura_cm: float | None = None,
    comprimento_cm: float | None = None,
    modelagem: str | None = None,
):
    """
    Busca produtos utilizando somente
    os filtros informados.

    O tamanho continua sendo tratado
    como texto livre do catálogo.
    """

    return (
        buscar_produto_por_categoria_tamanho_cor(
            categoria,
            tamanho,
            cor,
            largura_cm,
            comprimento_cm,
            modelagem,
        )
    )


@router.get(
    "/produtos/{id}",
    response_model=ProdutoResponse,
)
def buscar_produto(
    id: int,
):
    """Busca um único produto pelo ID."""

    produto = buscar_produto_por_id(
        id
    )

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    return produto


# ==========================================================
# GRADE DINÂMICA DO PRODUTO
# ==========================================================

@router.get(
    "/produtos/{id}/grade-tamanhos"
)
def grade_tamanhos_produto(
    id: int,
):
    """
    Retorna a grade real de tamanhos
    existente para o produto informado.

    A grade vem das variantes cadastradas
    no catálogo e não de uma enumeração
    fixa do VesteIA.
    """

    produto = buscar_produto_por_id(
        id
    )

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    grade = (
        obter_grade_tamanhos_produto(
            produto
        )
    )

    variantes = (
        obter_variantes_produto(
            produto
        )
    )

    return {
        "produto": {
            "id": produto.get("id"),
            "nome": produto.get("nome"),
            "cor": produto.get("cor"),
            "categoria": produto.get(
                "categoria"
            ),
            "modelagem": produto.get(
                "modelagem"
            ),
        },
        "grade_tamanhos": grade,
        "variantes": variantes,
        "quantidade_variantes": len(
            variantes
        ),
        "grade_dinamica": True,
        "tamanho_padrao_vesteia": False,
        "origem_grade": (
            "catalogo_produto"
        ),
    }


# ==========================================================
# MOTOR DE RECOMENDAÇÃO
# ==========================================================

@router.get("/recomendar-tamanho")
def recomendar_tamanho_endpoint(
    altura_cm: float,
    peso_kg: float,
    cintura_cm: float | None = None,
    preferencia_caimento: str | None = None,
    produto_id: int | None = None,
):
    """
    Calcula uma sugestão experimental
    de tamanho.

    Quando produto_id é informado,
    a grade vem automaticamente das
    variantes reais daquele produto.

    Sem produto_id, o motor mantém
    apenas o fallback demonstrativo
    temporário do MVP.
    """

    grade_tamanhos = None
    produto = None

    if produto_id is not None:

        produto = (
            buscar_produto_por_id(
                produto_id
            )
        )

        if produto is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Produto não encontrado"
                ),
            )

        grade_tamanhos = (
            obter_grade_tamanhos_produto(
                produto
            )
        )

        if not grade_tamanhos:
            raise HTTPException(
                status_code=400,
                detail=(
                    "O produto não possui "
                    "variantes de tamanho "
                    "disponíveis no catálogo."
                ),
            )

    tamanho_recomendado = (
        recomendar_tamanho(
            altura_cm=altura_cm,
            peso_kg=peso_kg,
            cintura_cm=cintura_cm,
            preferencia_caimento=(
                preferencia_caimento
            ),
            grade_tamanhos=(
                grade_tamanhos
            ),
        )
    )

    explicacao = (
        explicar_recomendacao(
            tamanho_recomendado=(
                tamanho_recomendado
            ),
            cintura_cm=cintura_cm,
            preferencia_caimento=(
                preferencia_caimento
            ),
            grade_tamanhos=(
                grade_tamanhos
            ),
        )
    )

    return {
        "produto": (
            {
                "id": produto.get("id"),
                "nome": produto.get(
                    "nome"
                ),
            }
            if produto
            else None
        ),
        "tamanho_recomendado": (
            tamanho_recomendado
        ),
        "grade_tamanhos": (
            grade_tamanhos
            or explicacao.get(
                "grade_tamanhos",
                [],
            )
        ),
        "grade_dinamica": (
            produto_id is not None
        ),
        "tamanho_padrao_vesteia": False,
        "motivos": (
            explicacao[
                "motivos"
            ]
        ),
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
    Recomenda variantes utilizando
    a grade real de cada produto.

    Cada modelo pode possuir uma grade
    completamente diferente.

    Exemplos:

    Produto A:
    PP, M, EXG, GG2

    Produto B:
    34, 36, 40, 44, 46

    Produto C:
    XS, S, M, XL, 3XL

    O VesteIA trabalha somente com
    as variantes realmente existentes.
    """

    # ======================================================
    # PERFIL
    # ======================================================

    if (
        altura_cm is None
        and peso_kg is None
    ):
        altura_cm = (
            perfil_usuario[
                "altura_cm"
            ]
        )

        peso_kg = (
            perfil_usuario[
                "peso_kg"
            ]
        )

        if cintura_cm is None:
            cintura_cm = (
                perfil_usuario[
                    "cintura_cm"
                ]
            )

    if (
        (altura_cm is None)
        != (peso_kg is None)
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Para recomendar o tamanho, "
                "informe altura e peso juntos."
            ),
        )

    possui_dados_recomendacao = (
        altura_cm is not None
        and peso_kg is not None
    )

    confianca = None

    if possui_dados_recomendacao:
        confianca = (
            calcular_confianca_recomendacao(
                altura_cm,
                peso_kg,
                cintura_cm,
            )
        )

    # ======================================================
    # CATÁLOGO SEM FILTRAR TAMANHO
    # ======================================================

    produtos_catalogo = (
        buscar_produto_por_categoria_tamanho_cor(
            categoria=categoria,
            tamanho=None,
            cor=None,
            largura_cm=None,
            comprimento_cm=None,
            modelagem=modelagem,
        )
    )

    if not produtos_catalogo:
        return {
            "mensagem": (
                "Nenhum produto foi encontrado "
                "para os filtros informados."
            ),
            "tamanho_recomendado": None,
            "confianca": confianca,
            "explicacao": None,
            "grade_dinamica": True,
            "tamanho_padrao_vesteia": False,
            "recomendacoes_por_produto": [],
            "produtos": [],
        }

    grupos = (
        _agrupar_produtos_por_modelo(
            produtos_catalogo
        )
    )

    produtos_recomendados = []
    recomendacoes_por_produto = []

    # ======================================================
    # RECOMENDAÇÃO POR MODELO
    # ======================================================

    for grupo in grupos:

        if not grupo:
            continue

        produto_referencia = grupo[0]

        grade_tamanhos = (
            obter_grade_tamanhos_produto(
                produto_referencia
            )
        )

        variantes = (
            obter_variantes_produto(
                produto_referencia
            )
        )

        tamanho_recomendado = None
        explicacao = None
        variante_recomendada = None

        if (
            possui_dados_recomendacao
            and grade_tamanhos
        ):
            tamanho_recomendado = (
                recomendar_tamanho(
                    altura_cm=altura_cm,
                    peso_kg=peso_kg,
                    cintura_cm=cintura_cm,
                    preferencia_caimento=(
                        preferencia_caimento
                    ),
                    grade_tamanhos=(
                        grade_tamanhos
                    ),
                )
            )

            explicacao = (
                explicar_recomendacao(
                    tamanho_recomendado=(
                        tamanho_recomendado
                    ),
                    cintura_cm=cintura_cm,
                    preferencia_caimento=(
                        preferencia_caimento
                    ),
                    grade_tamanhos=(
                        grade_tamanhos
                    ),
                )
            )

            variante_recomendada = (
                _buscar_variante_por_tamanho(
                    variantes,
                    tamanho_recomendado,
                )
            )

        recomendacao_modelo = {
            "produto": {
                "id_referencia": (
                    produto_referencia.get(
                        "id"
                    )
                ),
                "nome": (
                    produto_referencia.get(
                        "nome"
                    )
                ),
                "cor": (
                    produto_referencia.get(
                        "cor"
                    )
                ),
                "categoria": (
                    produto_referencia.get(
                        "categoria"
                    )
                ),
                "modelagem": (
                    produto_referencia.get(
                        "modelagem"
                    )
                ),
            },
            "grade_tamanhos": (
                grade_tamanhos
            ),
            "quantidade_variantes": (
                len(
                    variantes
                )
            ),
            "tamanho_recomendado": (
                tamanho_recomendado
            ),
            "variante_recomendada": (
                variante_recomendada
            ),
            "explicacao": (
                explicacao
            ),
            "grade_dinamica": True,
            "tamanho_padrao_vesteia": False,
        }

        recomendacoes_por_produto.append(
            recomendacao_modelo
        )

        # Quando há recomendação, retornamos
        # somente a variante selecionada
        # daquele modelo.

        if variante_recomendada:

            produto_saida = dict(
                variante_recomendada
            )

            analise = (
                verificar_compatibilidade_peca(
                    tamanho_recomendado=(
                        produto_saida.get(
                            "tamanho"
                        )
                    ),
                    largura_cm=(
                        produto_saida.get(
                            "largura_cm"
                        )
                    ),
                    comprimento_cm=(
                        produto_saida.get(
                            "comprimento_cm"
                        )
                    ),
                    modelagem=(
                        produto_saida.get(
                            "modelagem"
                        )
                    ),
                )
            )

            produto_saida[
                "observacoes"
            ] = analise[
                "observacoes"
            ]

            produto_saida[
                "grade_tamanhos"
            ] = grade_tamanhos

            produto_saida[
                "tamanho_recomendado"
            ] = tamanho_recomendado

            produtos_recomendados.append(
                produto_saida
            )

        # Sem dados corporais, preservamos
        # os produtos disponíveis para consulta.
        elif not possui_dados_recomendacao:

            for variante in variantes:

                produto_saida = dict(
                    variante
                )

                produto_saida[
                    "grade_tamanhos"
                ] = grade_tamanhos

                produtos_recomendados.append(
                    produto_saida
                )

    # ======================================================
    # COMPATIBILIDADE COM O FORMATO ANTIGO
    # ======================================================

    # Quando existe somente um modelo,
    # mantemos tamanho_recomendado e
    # explicacao também no topo da resposta.

    tamanho_recomendado_topo = None
    explicacao_topo = None

    if len(
        recomendacoes_por_produto
    ) == 1:

        tamanho_recomendado_topo = (
            recomendacoes_por_produto[
                0
            ].get(
                "tamanho_recomendado"
            )
        )

        explicacao_topo = (
            recomendacoes_por_produto[
                0
            ].get(
                "explicacao"
            )
        )

    if possui_dados_recomendacao:

        if produtos_recomendados:
            mensagem = (
                "Encontramos variantes compatíveis "
                "utilizando as grades reais "
                "disponíveis no catálogo."
            )

        else:
            mensagem = (
                "Os produtos foram encontrados, "
                "mas nenhuma variante pôde ser "
                "selecionada com os dados atuais."
            )

    else:
        mensagem = (
            "Perfil sem altura e peso completos. "
            "Confira as variantes disponíveis "
            "no catálogo."
        )

    return {
        "mensagem": mensagem,
        "tamanho_recomendado": (
            tamanho_recomendado_topo
        ),
        "confianca": confianca,
        "explicacao": (
            explicacao_topo
        ),
        "grade_dinamica": True,
        "tamanho_padrao_vesteia": False,
        "recomendacoes_por_produto": (
            recomendacoes_por_produto
        ),
        "produtos": (
            produtos_recomendados
        ),
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
    """
    Atualiza os dados corporais
    utilizados na recomendação.
    """

    perfil_usuario[
        "altura_cm"
    ] = altura_cm

    perfil_usuario[
        "peso_kg"
    ] = peso_kg

    perfil_usuario[
        "cintura_cm"
    ] = cintura_cm

    return {
        "mensagem": (
            "Perfil atualizado com sucesso"
        ),
        "perfil": perfil_usuario,
    }
