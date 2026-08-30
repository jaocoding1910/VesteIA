from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)

from app.models.sessao_provador import SessaoProvador

from app.services.catalogo import (
    buscar_produto_por_id,
    buscar_variacoes_produto,
)

from app.services.contexto_corpo_produto import (
    gerar_contexto_corpo_produto,
)

from app.services.compatibilidade_corpo_produto import (
    analisar_compatibilidade_corpo_produto,
)

from app.services.compatibilidade_dimensional import (
    analisar_compatibilidade_dimensional,
)

from app.services.resultado_dimensional import (
    gerar_resultado_dimensional,
)

from app.services.decisao_provador import (
    gerar_decisao_provador,
)

from app.services.contrato_provador import (
    gerar_contrato_provador_v1,
)

from app.services.recomendacao_tamanho_provador import (
    gerar_recomendacao_tamanho_provador,
)

from app.services.deteccao_pessoa import (
    detectar_pessoa,
)

from app.services.representacao_corporal import (
    gerar_representacao_corporal_v1,
)

from app.services.avatar_corporal import (
    gerar_avatar_corporal_v1,
)

from app.services.estado_renderizacao_avatar import (
    gerar_estado_renderizacao_avatar_v1,
)

from app.services.malha_corporal_2d import (
    gerar_malha_corporal_2d_v1,
)

from app.services.renderer_avatar_2d import (
    gerar_renderer_avatar_2d_v1,
)

from app.services.representacao_roupa import (
    gerar_representacao_roupa_v1,
)

from app.services.vestimenta_avatar_2d import (
    vestir_avatar_2d_v1,
)

from app.services.simulacao_caimento_visual import (
    simular_caimento_visual_v1,
)

from app.services.integracao_final_provador import (
    gerar_integracao_final_provador_v1,
)

from app.services.processamento_imagem import (
    analisar_imagem,
    avaliar_entrada_visual,
    avaliar_qualidade_foto,
    normalizar_imagem,
)

from app.services.provador import (
    adicionar_sessao_provador,
    atualizar_caminho_normalizado,
    atualizar_status_sessao,
    buscar_sessao_provador_por_id,
    listar_sessoes_provador,
)


router = APIRouter(
    prefix="/provador",
    tags=["Provador VesteIA"],
)


TAMANHO_MAXIMO_FOTO = (
    10 * 1024 * 1024
)

TIPOS_IMAGEM_PERMITIDOS = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

EXTENSOES_IMAGEM = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

PASTA_UPLOADS_PROVADOR = (
    BACKEND_DIR
    / "uploads"
    / "provador"
)


# ==========================================================
# PREFERÊNCIA DE CAIMENTO
# ==========================================================

def normalizar_preferencia_caimento(
    preferencia_caimento,
):
    """
    Normaliza a preferência recebida
    pelo frontend.

    Valores internos:
    - justo
    - padrao
    - solto
    """

    if not preferencia_caimento:
        return "padrao"

    preferencia = (
        str(
            preferencia_caimento
        )
        .strip()
        .lower()
    )

    mapa = {
        "justo": "justo",
        "ajustado": "justo",
        "slim": "justo",

        "padrao": "padrao",
        "padrão": "padrao",
        "normal": "padrao",
        "regular": "padrao",

        "solto": "solto",
        "amplo": "solto",
        "oversized": "solto",
    }

    return mapa.get(
        preferencia,
        "padrao",
    )


# ==========================================================
# ARMAZENAMENTO DA FOTO
# ==========================================================

def salvar_foto_localmente(
    conteudo: bytes,
    tipo_arquivo: str,
):
    """
    Salva a imagem utilizando
    um nome interno único.
    """

    PASTA_UPLOADS_PROVADOR.mkdir(
        parents=True,
        exist_ok=True,
    )

    extensao = (
        EXTENSOES_IMAGEM[
            tipo_arquivo
        ]
    )

    nome_interno = (
        f"{uuid4().hex}{extensao}"
    )

    caminho_absoluto = (
        PASTA_UPLOADS_PROVADOR
        / nome_interno
    )

    caminho_absoluto.write_bytes(
        conteudo
    )

    caminho_relativo = (
        Path("uploads")
        / "provador"
        / nome_interno
    )

    return (
        caminho_relativo.as_posix(),
        caminho_absoluto,
    )


def verificar_arquivo_sessao(
    sessao,
):
    """
    Verifica se a sessão possui
    uma imagem fisicamente disponível.
    """

    caminho_relativo = sessao.get(
        "caminho_arquivo"
    )

    if not caminho_relativo:
        return False

    caminho_absoluto = (
        BACKEND_DIR
        / caminho_relativo
    )

    return caminho_absoluto.is_file()


# ==========================================================
# PREPARAR SESSÃO
# ==========================================================

@router.post("/preparar")
async def preparar_experiencia(
    foto: UploadFile = File(...),
    produto_id: int = Form(...),
    modo: str = Form("foto"),
):
    """
    Recebe, valida e registra uma nova sessão
    foto-first do Provador VesteIA.

    Neste fluxo:
    - o usuário seleciona o produto;
    - envia sua foto;
    - não informa tamanho;
    - não informa medidas corporais;
    - o tamanho será analisado posteriormente
      pelo motor do VesteIA.
    """

    if modo != "foto":
        raise HTTPException(
            status_code=400,
            detail=(
                "Este endpoint atualmente aceita "
                "apenas o modo foto."
            ),
        )

    try:
        produto = (
            buscar_produto_por_id(
                produto_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "o produto selecionado."
            ),
        ) from erro

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "O produto selecionado "
                "não foi encontrado."
            ),
        )

    produto_nome = (
        produto.get("nome")
        or "Produto VesteIA"
    )

    if (
        foto.content_type
        not in TIPOS_IMAGEM_PERMITIDOS
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Formato de imagem "
                "não permitido."
            ),
        )

    conteudo_foto = (
        await foto.read()
    )

    tamanho_arquivo = len(
        conteudo_foto
    )

    if tamanho_arquivo == 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "A imagem enviada está vazia."
            ),
        )

    if (
        tamanho_arquivo
        > TAMANHO_MAXIMO_FOTO
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "A imagem deve ter "
                "no máximo 10 MB."
            ),
        )

    try:
        (
            caminho_relativo,
            caminho_absoluto,
        ) = salvar_foto_localmente(
            conteudo=conteudo_foto,
            tipo_arquivo=(
                foto.content_type
            ),
        )

    except OSError as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível armazenar "
                "a imagem do provador."
            ),
        ) from erro

    sessao = SessaoProvador(
        produto_id=produto_id,
        produto_nome=produto_nome,
        tamanho=None,
        modo=modo,
        nome_arquivo=(
            foto.filename
        ),
        tipo_arquivo=(
            foto.content_type
        ),
        tamanho_bytes=(
            tamanho_arquivo
        ),
        status=(
            "pronto_para_processar"
        ),
        caminho_arquivo=(
            caminho_relativo
        ),
    )

    try:
        registro = (
            adicionar_sessao_provador(
                sessao
            )
        )

    except Exception as erro:
        caminho_absoluto.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível registrar "
                "a sessão no PostgreSQL."
            ),
        ) from erro

    return {
        "sessao_id": (
            registro["id"]
        ),

        "criado_em": (
            registro["criado_em"]
        ),

        "status": "recebido",

        "status_processamento": (
            registro["status"]
        ),

        "pronto_para_processar": True,

        "modo": modo,

        "produto": {
            "id": (
                produto["id"]
            ),
            "nome": (
                produto["nome"]
            ),
            "categoria": (
                produto.get(
                    "categoria"
                )
            ),
            "cor": (
                produto.get(
                    "cor"
                )
            ),
            "modelagem": (
                produto.get(
                    "modelagem"
                )
            ),
            "tamanho_inicial": None,
            "tamanho_definido": False,
        },

        "fluxo": {
            "tipo": "foto_first",
            "entrada_corporal": "foto",
            "medidas_manuais_obrigatorias": False,
            "medidas_manuais_fornecidas": False,
            "tamanho_inicial_obrigatorio": False,
            "tamanho_sera_analisado": True,
            "refinamento_por_medidas_disponivel": False,
        },

        "arquivo": {
            "nome": (
                foto.filename
            ),
            "tipo": (
                foto.content_type
            ),
            "tamanho_bytes": (
                tamanho_arquivo
            ),
            "armazenado": True,
        },

        "proxima_etapa": {
            "acao": "analisar_foto",
            "descricao": (
                "A imagem está pronta para ser "
                "analisada pelo motor visual "
                "do VesteIA."
            ),
        },

        "mensagem": (
            "Foto recebida pelo VesteIA. "
            "Nenhum tamanho ou medida corporal "
            "foi solicitado nesta etapa."
        ),
    }


# ==========================================================
# LISTAR SESSÕES
# ==========================================================

@router.get("/sessoes")
def listar_sessoes():
    """
    Lista todas as sessões registradas.
    """

    try:
        return (
            listar_sessoes_provador()
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "as sessões do provador."
            ),
        ) from erro


# ==========================================================
# OBTER SESSÃO
# ==========================================================

@router.get(
    "/sessoes/{sessao_id}"
)
def obter_sessao(
    sessao_id: int,
):
    """
    Busca uma sessão e verifica
    a disponibilidade da imagem.
    """

    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    arquivo_disponivel = (
        verificar_arquivo_sessao(
            sessao
        )
    )

    pronto_para_processar = (
        sessao["status"]
        == "pronto_para_processar"
        and arquivo_disponivel
    )

    return {
        "sessao": sessao,
        "arquivo_disponivel": (
            arquivo_disponivel
        ),
        "pronto_para_processar": (
            pronto_para_processar
        ),
    }


# ==========================================================
# INICIAR PROCESSAMENTO
# ==========================================================

@router.post(
    "/sessoes/{sessao_id}/processar"
)
def iniciar_processamento(
    sessao_id: int,
):
    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    if not verificar_arquivo_sessao(
        sessao
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "A sessão não possui uma imagem "
                "disponível para processamento."
            ),
        )

    if (
        sessao["status"]
        == "processando"
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Esta sessão já está "
                "em processamento."
            ),
        )

    if (
        sessao["status"]
        != "pronto_para_processar"
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "A sessão não está em um estado "
                "válido para iniciar "
                "o processamento."
            ),
        )

    try:
        resultado = (
            atualizar_status_sessao(
                sessao_id=sessao_id,
                novo_status="processando",
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível atualizar "
                "o status da sessão."
            ),
        ) from erro

    return {
        "sessao_id": resultado["id"],
        "status_anterior": sessao["status"],
        "status_atual": resultado["status"],
        "mensagem": (
            "Processamento da sessão "
            "VesteIA iniciado com sucesso."
        ),
    }


# ==========================================================
# CONCLUIR PROCESSAMENTO
# ==========================================================

@router.post(
    "/sessoes/{sessao_id}/concluir"
)
def concluir_processamento(
    sessao_id: int,
):
    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    if (
        sessao["status"]
        == "processado"
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Esta sessão já foi processada."
            ),
        )

    if (
        sessao["status"]
        != "processando"
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Somente uma sessão em "
                "processamento pode ser concluída."
            ),
        )

    try:
        resultado = (
            atualizar_status_sessao(
                sessao_id=sessao_id,
                novo_status="processado",
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível concluir "
                "o processamento da sessão."
            ),
        ) from erro

    return {
        "sessao_id": resultado["id"],
        "status_anterior": sessao["status"],
        "status_atual": resultado["status"],
        "sucesso": True,
        "mensagem": (
            "Processamento da sessão "
            "VesteIA concluído com sucesso."
        ),
    }


# ==========================================================
# REGISTRAR FALHA
# ==========================================================

@router.post(
    "/sessoes/{sessao_id}/falhar"
)
def registrar_falha_processamento(
    sessao_id: int,
):
    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    if (
        sessao["status"]
        == "erro"
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Esta sessão já está "
                "marcada com erro."
            ),
        )

    if (
        sessao["status"]
        != "processando"
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Somente uma sessão em "
                "processamento pode ser "
                "marcada com erro."
            ),
        )

    try:
        resultado = (
            atualizar_status_sessao(
                sessao_id=sessao_id,
                novo_status="erro",
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível registrar "
                "a falha de processamento."
            ),
        ) from erro

    return {
        "sessao_id": resultado["id"],
        "status_anterior": sessao["status"],
        "status_atual": resultado["status"],
        "sucesso": False,
        "mensagem": (
            "Falha de processamento registrada "
            "na sessão VesteIA."
        ),
    }


# ==========================================================
# ANALISAR IMAGEM
# ==========================================================

@router.get(
    "/sessoes/{sessao_id}/analisar-imagem"
)
def analisar_imagem_sessao(
    sessao_id: int,
):
    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    caminho_relativo = sessao.get(
        "caminho_arquivo"
    )

    if not caminho_relativo:
        raise HTTPException(
            status_code=400,
            detail=(
                "A sessão não possui uma "
                "imagem armazenada."
            ),
        )

    caminho_absoluto = (
        BACKEND_DIR
        / caminho_relativo
    )

    try:
        analise = analisar_imagem(
            caminho_absoluto
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=404,
            detail=(
                "O arquivo físico da sessão "
                "não foi encontrado."
            ),
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        ) from erro

    return {
        "sessao_id": sessao["id"],
        "produto": sessao["produto_nome"],
        "status": sessao["status"],
        "arquivo": {
            "nome_original": (
                sessao["nome_arquivo"]
            ),
            "caminho": (
                sessao["caminho_arquivo"]
            ),
        },
        "analise_imagem": analise,
        "mensagem": (
            "Imagem analisada pelo processador "
            "do VesteIA com sucesso."
        ),
    }


# ==========================================================
# NORMALIZAR IMAGEM
# ==========================================================

@router.post(
    "/sessoes/{sessao_id}/normalizar-imagem"
)
def normalizar_imagem_sessao(
    sessao_id: int,
):
    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    caminho_original = sessao.get(
        "caminho_arquivo"
    )

    if not caminho_original:
        raise HTTPException(
            status_code=400,
            detail=(
                "A sessão não possui uma "
                "imagem armazenada."
            ),
        )

    caminho_absoluto_original = (
        BACKEND_DIR
        / caminho_original
    )

    if not caminho_absoluto_original.is_file():
        raise HTTPException(
            status_code=404,
            detail=(
                "O arquivo físico original "
                "não foi encontrado."
            ),
        )

    nome_base = (
        caminho_absoluto_original.stem
    )

    caminho_relativo_normalizado = (
        Path("uploads")
        / "provador"
        / "normalizadas"
        / f"{nome_base}_normalizado.jpg"
    )

    caminho_absoluto_normalizado = (
        BACKEND_DIR
        / caminho_relativo_normalizado
    )

    try:
        resultado_normalizacao = (
            normalizar_imagem(
                caminho_origem=(
                    caminho_absoluto_original
                ),
                caminho_destino=(
                    caminho_absoluto_normalizado
                ),
            )
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=404,
            detail=(
                "O arquivo original da sessão "
                "não foi encontrado."
            ),
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        ) from erro

    try:
        registro = (
            atualizar_caminho_normalizado(
                sessao_id=sessao_id,
                caminho_normalizado=(
                    caminho_relativo_normalizado
                    .as_posix()
                ),
            )
        )

    except Exception as erro:
        caminho_absoluto_normalizado.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "A imagem foi normalizada, "
                "mas não foi possível atualizar "
                "a sessão."
            ),
        ) from erro

    return {
        "sessao_id": registro["id"],
        "arquivo_original": caminho_original,
        "arquivo_normalizado": (
            registro[
                "caminho_normalizado"
            ]
        ),
        "normalizacao": (
            resultado_normalizacao
        ),
        "mensagem": (
            "Imagem normalizada para o padrão "
            "interno do VesteIA com sucesso."
        ),
    }


# ==========================================================
# ENTRADA VISUAL
# ==========================================================

@router.get(
    "/sessoes/{sessao_id}/entrada-visual"
)
def preparar_entrada_visual(
    sessao_id: int,
):
    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    caminho_normalizado = sessao.get(
        "caminho_normalizado"
    )

    if not caminho_normalizado:
        raise HTTPException(
            status_code=409,
            detail=(
                "A sessão ainda não possui uma "
                "imagem normalizada. Normalize "
                "a imagem antes de preparar "
                "a entrada visual."
            ),
        )

    caminho_absoluto = (
        BACKEND_DIR
        / caminho_normalizado
    )

    try:
        avaliacao = (
            avaliar_entrada_visual(
                caminho_absoluto
            )
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=404,
            detail=(
                "A referência da imagem "
                "normalizada existe, mas o "
                "arquivo físico não foi encontrado."
            ),
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        ) from erro

    return {
        "sessao_id": sessao["id"],
        "produto": {
            "id": sessao["produto_id"],
            "nome": sessao["produto_nome"],
            "tamanho": sessao["tamanho"],
        },
        "status_sessao": sessao["status"],
        "entrada_visual": {
            "arquivo": caminho_normalizado,
            "origem": "imagem_normalizada",
            **avaliacao,
        },
        "mensagem": (
            "Entrada visual do Provador "
            "VesteIA preparada com sucesso."
        ),
    }


# ==========================================================
# AVALIAÇÃO DA FOTO
# ==========================================================

@router.get(
    "/sessoes/{sessao_id}/avaliar-foto"
)
def avaliar_foto_provador(
    sessao_id: int,
):
    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    caminho_normalizado = sessao.get(
        "caminho_normalizado"
    )

    if not caminho_normalizado:
        raise HTTPException(
            status_code=409,
            detail=(
                "A sessão ainda não possui "
                "uma imagem normalizada."
            ),
        )

    caminho_absoluto = (
        BACKEND_DIR
        / caminho_normalizado
    )

    try:
        avaliacao = (
            avaliar_qualidade_foto(
                caminho_absoluto
            )
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=404,
            detail=(
                "A imagem normalizada "
                "da sessão não foi encontrada."
            ),
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        ) from erro

    return {
        "sessao_id": sessao["id"],
        "produto": {
            "id": sessao["produto_id"],
            "nome": sessao["produto_nome"],
            "tamanho": sessao["tamanho"],
        },
        "avaliacao_foto": avaliacao,
        "mensagem": (
            "Qualidade técnica da foto "
            "avaliada pelo VesteIA."
        ),
    }


# ==========================================================
# DETECÇÃO HUMANA
# ==========================================================

@router.get(
    "/sessoes/{sessao_id}/detectar-pessoa"
)
def detectar_pessoa_sessao(
    sessao_id: int,
    preferencia_caimento: str = Query(
        default="padrao",
        description=(
            "Preferência de caimento: "
            "justo, padrao ou solto."
        ),
    ),
):
    preferencia_caimento = (
        normalizar_preferencia_caimento(
            preferencia_caimento
        )
    )

    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    try:
        produto = (
            buscar_produto_por_id(
                sessao["produto_id"]
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "o produto da sessão."
            ),
        ) from erro

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "O produto associado à sessão "
                "não foi encontrado."
            ),
        )

    caminho_normalizado = sessao.get(
        "caminho_normalizado"
    )

    if not caminho_normalizado:
        raise HTTPException(
            status_code=409,
            detail=(
                "Normalize a imagem antes "
                "de executar a detecção humana."
            ),
        )

    caminho_absoluto = (
        BACKEND_DIR
        / caminho_normalizado
    )

    try:
        deteccao = detectar_pessoa(
            caminho_absoluto,
            altura_cm=None,
            modelagem=produto.get(
                "modelagem"
            ),
            preferencia_caimento=(
                preferencia_caimento
            ),
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro),
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        ) from erro

    representacao_corporal = (
        gerar_representacao_corporal_v1(
            deteccao
        )
    )

    avatar_corporal = (
        gerar_avatar_corporal_v1(
            representacao_corporal
        )
    )

    contexto_corpo_produto = (
        gerar_contexto_corpo_produto(
            produto,
            deteccao,
        )
    )

    return {
        "sessao_id": sessao["id"],

        "preferencia_caimento": (
            preferencia_caimento
        ),

        "produto": {
            "id": produto["id"],
            "nome": produto["nome"],
            "tamanho": produto["tamanho"],
            "categoria": produto["categoria"],
            "cor": produto["cor"],
            "largura_cm": produto["largura_cm"],
            "comprimento_cm": produto["comprimento_cm"],
            "modelagem": produto["modelagem"],
        },

        "deteccao_humana": (
            deteccao
        ),

        "representacao_corporal": (
            representacao_corporal
        ),

        "avatar_corporal": (
            avatar_corporal
        ),

        "contexto_corpo_produto": (
            contexto_corpo_produto
        ),

        "mensagem": (
            "Detecção humana, representação "
            "corporal e Avatar Corporal V1 "
            "preparados somente com a fotografia."
        ),
    }


# ==========================================================
# PIPELINE AUTOMÁTICO
# ==========================================================

@router.post(
    "/sessoes/{sessao_id}/executar"
)
def executar_pipeline_provador(
    sessao_id: int,
    preferencia_caimento: str = Query(
        default="padrao",
        description=(
            "Preferência de caimento: "
            "justo, padrao ou solto."
        ),
    ),
):
    """
    Orquestra automaticamente
    o pipeline principal do VesteIA.

    Fluxo foto-only:
    foto
    -> detecção
    -> representação corporal
    -> Avatar Corporal V1
    -> Estado de Renderização V1
    -> Malha Corporal 2D V1
    -> Renderer do Avatar 2D V1
    -> Representação da Roupa V1
    -> análise corpo-produto
    """

    preferencia_caimento = (
        normalizar_preferencia_caimento(
            preferencia_caimento
        )
    )

    # ======================================================
    # SESSÃO
    # ======================================================

    try:
        sessao = (
            buscar_sessao_provador_por_id(
                sessao_id
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        ) from erro

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Sessão do provador "
                "não encontrada."
            ),
        )

    # ======================================================
    # NORMALIZAÇÃO
    # ======================================================

    caminho_normalizado = sessao.get(
        "caminho_normalizado"
    )

    normalizacao_executada = False

    if not caminho_normalizado:

        caminho_original = sessao.get(
            "caminho_arquivo"
        )

        if not caminho_original:
            raise HTTPException(
                status_code=400,
                detail=(
                    "A sessão não possui "
                    "imagem armazenada."
                ),
            )

        caminho_absoluto_original = (
            BACKEND_DIR
            / caminho_original
        )

        if not caminho_absoluto_original.is_file():
            raise HTTPException(
                status_code=404,
                detail=(
                    "O arquivo físico original "
                    "não foi encontrado."
                ),
            )

        nome_base = (
            caminho_absoluto_original.stem
        )

        caminho_relativo_normalizado = (
            Path("uploads")
            / "provador"
            / "normalizadas"
            / f"{nome_base}_normalizado.jpg"
        )

        caminho_absoluto_normalizado = (
            BACKEND_DIR
            / caminho_relativo_normalizado
        )

        try:
            normalizar_imagem(
                caminho_origem=(
                    caminho_absoluto_original
                ),
                caminho_destino=(
                    caminho_absoluto_normalizado
                ),
            )

        except FileNotFoundError as erro:
            raise HTTPException(
                status_code=404,
                detail=str(erro),
            ) from erro

        except ValueError as erro:
            raise HTTPException(
                status_code=422,
                detail=str(erro),
            ) from erro

        try:
            atualizar_caminho_normalizado(
                sessao_id=sessao_id,
                caminho_normalizado=(
                    caminho_relativo_normalizado
                    .as_posix()
                ),
            )

        except Exception as erro:
            caminho_absoluto_normalizado.unlink(
                missing_ok=True
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "A imagem foi normalizada, "
                    "mas a sessão não pôde "
                    "ser atualizada."
                ),
            ) from erro

        caminho_normalizado = (
            caminho_relativo_normalizado
            .as_posix()
        )

        normalizacao_executada = True

    caminho_absoluto = (
        BACKEND_DIR
        / caminho_normalizado
    )

    # ======================================================
    # PRODUTO
    # ======================================================

    try:
        produto = (
            buscar_produto_por_id(
                sessao["produto_id"]
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "o produto da sessão."
            ),
        ) from erro

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "O produto associado à sessão "
                "não foi encontrado."
            ),
        )

    # ======================================================
    # DETECÇÃO CORPORAL FOTO-ONLY
    # ======================================================

    try:
        deteccao = detectar_pessoa(
            caminho_absoluto,

            altura_cm=None,

            modelagem=produto.get(
                "modelagem"
            ),

            preferencia_caimento=(
                preferencia_caimento
            ),
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro),
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        ) from erro

    # ======================================================
    # REPRESENTAÇÃO CORPORAL FOTO-ONLY V1
    # ======================================================

    representacao_corporal = (
        gerar_representacao_corporal_v1(
            deteccao
        )
    )

    # ======================================================
    # AVATAR CORPORAL V1
    # ======================================================

    avatar_corporal = (
        gerar_avatar_corporal_v1(
            representacao_corporal
        )
    )

    # ======================================================
    # ESTADO DE RENDERIZAÇÃO DO AVATAR V1
    # ======================================================

    estado_renderizacao_avatar = (
        gerar_estado_renderizacao_avatar_v1(
            avatar_corporal
        )
    )

    # ======================================================
    # MALHA CORPORAL 2D V1
    # ======================================================

    malha_corporal_2d = (
        gerar_malha_corporal_2d_v1(
            deteccao=deteccao,
            estado_renderizacao_avatar=(
                estado_renderizacao_avatar
            ),
        )
    )

    # ======================================================
    # RENDERER DO AVATAR 2D V1
    # ======================================================

    renderer_avatar_2d = (
        gerar_renderer_avatar_2d_v1(
            malha_corporal_2d
        )
    )

    # ======================================================
    # REPRESENTAÇÃO DA ROUPA V1
    # ======================================================

    representacao_roupa = (
        gerar_representacao_roupa_v1(
            produto=produto
        )
    )

    # ======================================================
    # VESTIMENTA DO AVATAR 2D V1
    # ======================================================

    vestimenta_avatar_2d = (
    vestir_avatar_2d_v1(
        renderer_avatar_2d=(
            renderer_avatar_2d
           ),
        representacao_roupa=(
            representacao_roupa
            ),
        )
    )

    # ======================================================
    # SIMULAÇÃO VISUAL DE CAIMENTO V1
    # ======================================================

    simulacao_caimento_visual = (
        simular_caimento_visual_v1(
        vestimenta_avatar_2d=(
            vestimenta_avatar_2d
            ),

        representacao_roupa=(
            representacao_roupa
            ),

        preferencia_caimento=(
            preferencia_caimento
            ),
        )
    )

    # ======================================================
    # INTEGRAÇÃO FINAL DO PROVADOR V1
    # ======================================================

    integracao_final_provador = (
        gerar_integracao_final_provador_v1(
        renderer_avatar_2d=(
            renderer_avatar_2d
            ),

        representacao_roupa=(
            representacao_roupa
            ),

        vestimenta_avatar_2d=(
            vestimenta_avatar_2d
            ),

        simulacao_caimento_visual=(
            simulacao_caimento_visual
            ),
        )
    )

    # ======================================================
    # CONTEXTO CORPO X PRODUTO
    # ======================================================

    contexto_corpo_produto = (
        gerar_contexto_corpo_produto(
            produto,
            deteccao,
        )
    )

    # ======================================================
    # COMPATIBILIDADE VISUAL
    # ======================================================

    compatibilidade_corpo_produto = (
        analisar_compatibilidade_corpo_produto(
            contexto_corpo_produto
        )
    )

    # ======================================================
    # COMPATIBILIDADE DIMENSIONAL
    # ======================================================

    compatibilidade_dimensional = (
        analisar_compatibilidade_dimensional(
            contexto_corpo_produto,
            deteccao,
        )
    )

    # ======================================================
    # RESULTADO DIMENSIONAL
    # ======================================================

    resultado_dimensional = (
        gerar_resultado_dimensional(
            compatibilidade_dimensional
        )
    )

    # ======================================================
    # VARIAÇÕES DO PRODUTO
    # ======================================================

    try:
        variacoes_produto = (
            buscar_variacoes_produto(
                produto
            )
        )

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "as variações de tamanho "
                "do produto."
            ),
        ) from erro

    # ======================================================
    # RECOMENDAÇÃO EXPERIMENTAL
    # ======================================================

    recomendacao_tamanho_provador = (
        gerar_recomendacao_tamanho_provador(
            variacoes_produto=(
                variacoes_produto
            ),

            deteccao=(
                deteccao
            ),

            preferencia_caimento=(
                preferencia_caimento
            ),
        )
    )

    # ======================================================
    # DECISÃO CONSOLIDADA
    # ======================================================

    decisao_provador = (
        gerar_decisao_provador(
            resumo_provador=(
                deteccao.get(
                    "resumo_provador"
                )
            ),

            compatibilidade_corpo_produto=(
                compatibilidade_corpo_produto
            ),

            compatibilidade_dimensional=(
                compatibilidade_dimensional
            ),

            resultado_dimensional=(
                resultado_dimensional
            ),

            recomendacao_tamanho_provador=(
                recomendacao_tamanho_provador
            ),
        )
    )

    # ======================================================
    # CONTRATO PROVADOR V1
    # ======================================================

    contrato_provador = (
        gerar_contrato_provador_v1(
            sessao_id=(
                sessao_id
            ),

            produto=(
                produto
            ),

            variacoes_produto=(
                variacoes_produto
            ),

            decisao_provador=(
                decisao_provador
            ),

            recomendacao_tamanho_provador=(
                recomendacao_tamanho_provador
            ),

            deteccao=(
                deteccao
            ),

            preferencia_caimento=(
                preferencia_caimento
            ),
        )
    )

    # ======================================================
    # RESPOSTA FINAL
    # ======================================================

    return {
        "sessao_id": (
            sessao_id
        ),

        "preferencia_caimento": (
            preferencia_caimento
        ),

        "modo_analise": {
            "tipo": "foto_only",
            "medidas_manuais_fornecidas": False,
            "altura_manual_fornecida": False,
            "usa_altura_salva_perfil": False,
        },

        "pipeline": {
            "normalizacao": (
                "executada"
                if normalizacao_executada
                else "ja_disponivel"
            ),

            "produto": (
                "carregado"
            ),

            "modelagem_produto": (
                "aplicada_na_deteccao"
            ),

            "deteccao": (
                "concluida"
            ),

            "representacao_corporal_v1": (
                "concluida"
            ),

            "avatar_corporal_v1": (
                "concluido"
            ),

            "estado_renderizacao_avatar_v1": (
                "concluido"
            ),

            "malha_corporal_2d_v1": (
                "concluida"
            ),

            "renderer_avatar_2d_v1": (
                "concluido"
            ),

            "representacao_roupa_v1": (
                "concluida"
                if representacao_roupa.get(
                    "pronta_para_vestir_avatar",
                    False,
                )
                else "indisponivel"
            ),

            "vestimenta_avatar_2d_v1": (
                "concluida"
                if vestimenta_avatar_2d.get(
                    "vestida_no_avatar",
                    False,
                )
                else "indisponivel"
            ),

            "simulacao_caimento_visual_v1": (
                "concluida"
                if simulacao_caimento_visual.get(
                    "caimento_simulado",
                    False,
                )
                else "indisponivel"
            ),

            "integracao_final_provador_v1": (
                "concluida"
                if integracao_final_provador.get(
                    "integracao_completa",
                    False,
                )
                else "parcial"
            ),

            "contexto_corpo_produto": (
                "concluido"
            ),

            "compatibilidade_corpo_produto": (
                "concluida"
            ),

            "compatibilidade_dimensional": (
                "concluida"
            ),

            "resultado_dimensional": (
                "concluido"
            ),

            "variacoes_produto": (
                "concluidas"
            ),

            "preferencia_caimento": (
                "aplicada"
            ),

            "recomendacao_tamanho_provador": (
                "concluida"
            ),

            "decisao_provador": (
                "concluida"
            ),

            "contrato_provador_v1": (
                "concluido"
            ),
        },

        "produto": {
            "id": produto["id"],
            "nome": produto["nome"],
            "tamanho": produto["tamanho"],
            "categoria": produto["categoria"],
            "cor": produto["cor"],
            "largura_cm": produto["largura_cm"],
            "comprimento_cm": produto["comprimento_cm"],
            "modelagem": produto["modelagem"],
        },

        "variacoes_produto": (
            variacoes_produto
        ),

        "resumo_provador": (
            deteccao.get(
                "resumo_provador"
            )
        ),

        "resultado_captura": (
            deteccao.get(
                "resultado_captura"
            )
        ),

        "controle_fluxo_provador": (
            deteccao.get(
                "controle_fluxo_provador"
            )
        ),

        "representacao_corporal": (
            representacao_corporal
        ),

        "avatar_corporal": (
            avatar_corporal
        ),

        "estado_renderizacao_avatar": (
            estado_renderizacao_avatar
        ),

        "malha_corporal_2d": (
            malha_corporal_2d
        ),

        "renderer_avatar_2d": (
            renderer_avatar_2d
        ),

        "representacao_roupa": (
            representacao_roupa
        ),

        "vestimenta_avatar_2d": (
            vestimenta_avatar_2d
        ),

        "simulacao_caimento_visual": (
            simulacao_caimento_visual
        ),

        "integracao_final_provador": (
            integracao_final_provador
        ),

        "contexto_corpo_produto": (
            contexto_corpo_produto
        ),

        "compatibilidade_corpo_produto": (
            compatibilidade_corpo_produto
        ),

        "compatibilidade_dimensional": (
            compatibilidade_dimensional
        ),

        "resultado_dimensional": (
            resultado_dimensional
        ),

        "recomendacao_tamanho_provador": (
            recomendacao_tamanho_provador
        ),

        "decisao_provador": (
            decisao_provador
        ),

        "contrato_provador": (
            contrato_provador
        ),

        "deteccao_humana": (
            deteccao
        ),

        "mensagem": (
            "Pipeline foto-only executado "
            "com representação corporal, "
            "Avatar Corporal V1 e "
            "Representação da Roupa V1, "
            "sem utilizar automaticamente "
            "altura, peso, cintura ou outras "
            "medidas salvas no perfil."
        ),
    }


# ==========================================================
# RESULTADO ENXUTO DO PROVADOR
# ==========================================================

@router.post(
    "/sessoes/{sessao_id}/resultado"
)
def obter_resultado_provador(
    sessao_id: int,
    preferencia_caimento: str = Query(
        default="padrao",
        description=(
            "Preferência de caimento: "
            "justo, padrao ou solto."
        ),
    ),
):
    """
    Executa o mesmo pipeline oficial
    e retorna o contrato enxuto
    do Provador VesteIA.
    """

    preferencia_caimento = (
        normalizar_preferencia_caimento(
            preferencia_caimento
        )
    )

    resultado_pipeline = (
        executar_pipeline_provador(
            sessao_id=(
                sessao_id
            ),
            preferencia_caimento=(
                preferencia_caimento
            ),
        )
    )

    contrato_provador = (
        resultado_pipeline.get(
            "contrato_provador"
        )
        or {}
    )

    representacao_corporal = (
        resultado_pipeline.get(
            "representacao_corporal"
        )
        or {}
    )

    avatar_corporal = (
        resultado_pipeline.get(
            "avatar_corporal"
        )
        or {}
    )

    representacao_roupa = (
        resultado_pipeline.get(
            "representacao_roupa"
        )
        or {}
    )

    vestimenta_avatar_2d = (
    resultado_pipeline.get(
        "vestimenta_avatar_2d"
        )
        or {}
    )

    simulacao_caimento_visual = (
        resultado_pipeline.get(
            "simulacao_caimento_visual"
        )
        or {}
    )

    integracao_final_provador = (
    resultado_pipeline.get(
        "integracao_final_provador"
        )
        or {}
    )

    if not contrato_provador:
        raise HTTPException(
            status_code=500,
            detail=(
                "O pipeline foi executado, "
                "mas o contrato Provador V1 "
                "não foi gerado."
            ),
        )

    return {
        "sessao_id": (
            sessao_id
        ),

        "preferencia_caimento": (
            preferencia_caimento
        ),

        "modo_analise": (
            resultado_pipeline.get(
                "modo_analise"
            )
        ),

        "versao_contrato": (
            contrato_provador.get(
                "versao_contrato"
            )
        ),

        "status": (
            contrato_provador.get(
                "status"
            )
        ),

        "pode_continuar": (
            contrato_provador.get(
                "pode_continuar",
                False,
            )
        ),

        "representacao_corporal": (
            representacao_corporal
        ),

        "avatar_corporal": (
            avatar_corporal
        ),

        "representacao_roupa": (
            representacao_roupa
        ),

        "vestimenta_avatar_2d": (
            vestimenta_avatar_2d
        ),

        "simulacao_caimento_visual": (
            simulacao_caimento_visual
        ),

        "contrato_provador": (
            contrato_provador
        ),

        "mensagem": (
            "Resultado enxuto do "
            "Provador VesteIA preparado "
            "em modo foto-only."
        ),
    }