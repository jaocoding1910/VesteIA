from app.services.processamento_imagem import (analisar_imagem, normalizar_imagem,)
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.models.sessao_provador import SessaoProvador
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


TAMANHO_MAXIMO_FOTO = 10 * 1024 * 1024

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


BACKEND_DIR = Path(__file__).resolve().parents[2]

PASTA_UPLOADS_PROVADOR = (
    BACKEND_DIR
    / "uploads"
    / "provador"
)


def salvar_foto_localmente(
    conteudo: bytes,
    tipo_arquivo: str,
):
    """
    Salva a imagem utilizando um nome interno único.
    """

    PASTA_UPLOADS_PROVADOR.mkdir(
        parents=True,
        exist_ok=True,
    )

    extensao = EXTENSOES_IMAGEM[tipo_arquivo]

    nome_interno = f"{uuid4().hex}{extensao}"

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


def verificar_arquivo_sessao(sessao):
    """
    Verifica se a sessão possui uma imagem
    fisicamente disponível no backend.
    """

    caminho_relativo = sessao["caminho_arquivo"]

    if not caminho_relativo:
        return False

    caminho_absoluto = (
        BACKEND_DIR
        / caminho_relativo
    )

    return caminho_absoluto.is_file()


@router.post("/preparar")
async def preparar_experiencia(
    foto: UploadFile = File(...),
    produto_id: int = Form(...),
    produto_nome: str = Form(...),
    tamanho: str = Form(...),
    modo: str = Form("foto"),
):
    """
    Recebe, valida e registra uma nova
    sessão do Provador VesteIA.
    """

    if modo != "foto":
        raise HTTPException(
            status_code=400,
            detail=(
                "Este endpoint atualmente aceita "
                "apenas o modo foto."
            ),
        )

    if foto.content_type not in TIPOS_IMAGEM_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Formato de imagem não permitido.",
        )

    conteudo_foto = await foto.read()

    tamanho_arquivo = len(
        conteudo_foto
    )

    if tamanho_arquivo == 0:
        raise HTTPException(
            status_code=400,
            detail="A imagem enviada está vazia.",
        )

    if tamanho_arquivo > TAMANHO_MAXIMO_FOTO:
        raise HTTPException(
            status_code=400,
            detail="A imagem deve ter no máximo 10 MB.",
        )

    try:
        (
            caminho_relativo,
            caminho_absoluto,
        ) = salvar_foto_localmente(
            conteudo=conteudo_foto,
            tipo_arquivo=foto.content_type,
        )

    except OSError:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível armazenar "
                "a imagem do provador."
            ),
        )

    sessao = SessaoProvador(
        produto_id=produto_id,
        produto_nome=produto_nome,
        tamanho=tamanho,
        modo=modo,
        nome_arquivo=foto.filename,
        tipo_arquivo=foto.content_type,
        tamanho_bytes=tamanho_arquivo,
        status="pronto_para_processar",
        caminho_arquivo=caminho_relativo,
    )

    try:
        registro = adicionar_sessao_provador(
            sessao
        )

    except Exception:
        caminho_absoluto.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível registrar "
                "a sessão no PostgreSQL."
            ),
        )

    return {
        "sessao_id": registro["id"],
        "criado_em": registro["criado_em"],
        "status": "recebido",
        "status_processamento": registro["status"],
        "pronto_para_processar": True,
        "modo": modo,
        "produto": {
            "id": produto_id,
            "nome": produto_nome,
            "tamanho": tamanho,
        },
        "arquivo": {
            "nome": foto.filename,
            "tipo": foto.content_type,
            "tamanho_bytes": tamanho_arquivo,
            "armazenado": True,
        },
        "mensagem": (
            "Sessão do Provador VesteIA registrada "
            "e imagem armazenada com sucesso."
        ),
    }


@router.get("/sessoes")
def listar_sessoes():
    """
    Lista todas as sessões registradas.
    """

    try:
        return listar_sessoes_provador()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "as sessões do provador."
            ),
        )


@router.get("/sessoes/{sessao_id}")
def obter_sessao(sessao_id: int):
    """
    Busca uma sessão e verifica
    a disponibilidade da imagem.
    """

    try:
        sessao = buscar_sessao_provador_por_id(
            sessao_id
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        )

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão do provador não encontrada.",
        )

    arquivo_disponivel = verificar_arquivo_sessao(
        sessao
    )

    pronto_para_processar = (
        sessao["status"] == "pronto_para_processar"
        and arquivo_disponivel
    )

    return {
        "sessao": sessao,
        "arquivo_disponivel": arquivo_disponivel,
        "pronto_para_processar": pronto_para_processar,
    }


@router.post("/sessoes/{sessao_id}/processar")
def iniciar_processamento(sessao_id: int):
    """
    Valida a sessão e inicia seu ciclo
    de processamento.
    """

    try:
        sessao = buscar_sessao_provador_por_id(
            sessao_id
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        )

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão do provador não encontrada.",
        )

    if not verificar_arquivo_sessao(sessao):
        raise HTTPException(
            status_code=400,
            detail=(
                "A sessão não possui uma imagem "
                "disponível para processamento."
            ),
        )

    if sessao["status"] == "processando":
        raise HTTPException(
            status_code=409,
            detail=(
                "Esta sessão já está em processamento."
            ),
        )

    if sessao["status"] != "pronto_para_processar":
        raise HTTPException(
            status_code=409,
            detail=(
                "A sessão não está em um estado "
                "válido para iniciar o processamento."
            ),
        )

    try:
        resultado = atualizar_status_sessao(
            sessao_id=sessao_id,
            novo_status="processando",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível atualizar "
                "o status da sessão."
            ),
        )

    return {
        "sessao_id": resultado["id"],
        "status_anterior": sessao["status"],
        "status_atual": resultado["status"],
        "mensagem": (
            "Processamento da sessão "
            "VesteIA iniciado com sucesso."
        ),
    }


@router.post("/sessoes/{sessao_id}/concluir")
def concluir_processamento(sessao_id: int):
    """
    Finaliza com sucesso uma sessão que
    atualmente está em processamento.
    """

    try:
        sessao = buscar_sessao_provador_por_id(
            sessao_id
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        )

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão do provador não encontrada.",
        )

    if sessao["status"] == "processado":
        raise HTTPException(
            status_code=409,
            detail=(
                "Esta sessão já foi processada."
            ),
        )

    if sessao["status"] != "processando":
        raise HTTPException(
            status_code=409,
            detail=(
                "Somente uma sessão em processamento "
                "pode ser concluída."
            ),
        )

    try:
        resultado = atualizar_status_sessao(
            sessao_id=sessao_id,
            novo_status="processado",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível concluir "
                "o processamento da sessão."
            ),
        )

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


@router.post("/sessoes/{sessao_id}/falhar")
def registrar_falha_processamento(sessao_id: int):
    """
    Marca como erro uma sessão que
    atualmente está em processamento.
    """

    try:
        sessao = buscar_sessao_provador_por_id(
            sessao_id
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        )

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão do provador não encontrada.",
        )

    if sessao["status"] == "erro":
        raise HTTPException(
            status_code=409,
            detail=(
                "Esta sessão já está marcada com erro."
            ),
        )

    if sessao["status"] != "processando":
        raise HTTPException(
            status_code=409,
            detail=(
                "Somente uma sessão em processamento "
                "pode ser marcada com erro."
            ),
        )

    try:
        resultado = atualizar_status_sessao(
            sessao_id=sessao_id,
            novo_status="erro",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível registrar "
                "a falha de processamento."
            ),
        )

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


@router.get("/sessoes/{sessao_id}/analisar-imagem")
def analisar_imagem_sessao(sessao_id: int):
    """
    Analisa tecnicamente a imagem armazenada
    em uma sessão do Provador VesteIA.
    """

    try:
        sessao = buscar_sessao_provador_por_id(
            sessao_id
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        )

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão do provador não encontrada.",
        )

    caminho_relativo = sessao["caminho_arquivo"]

    if not caminho_relativo:
        raise HTTPException(
            status_code=400,
            detail=(
                "A sessão não possui uma imagem "
                "armazenada."
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

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=(
                "O arquivo físico da sessão "
                "não foi encontrado."
            ),
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        )

    return {
        "sessao_id": sessao["id"],
        "produto": sessao["produto_nome"],
        "status": sessao["status"],
        "arquivo": {
            "nome_original": sessao["nome_arquivo"],
            "caminho": sessao["caminho_arquivo"],
        },
        "analise_imagem": analise,
        "mensagem": (
            "Imagem analisada pelo processador "
            "do VesteIA com sucesso."
        ),
    }


@router.post(
    "/sessoes/{sessao_id}/normalizar-imagem"
)
def normalizar_imagem_sessao(sessao_id: int):
    """
    Cria uma versão JPEG/RGB padronizada
    da imagem de uma sessão.
    """

    try:
        sessao = buscar_sessao_provador_por_id(
            sessao_id
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível consultar "
                "a sessão do provador."
            ),
        )

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão do provador não encontrada.",
        )

    caminho_original = sessao[
        "caminho_arquivo"
    ]

    if not caminho_original:
        raise HTTPException(
            status_code=400,
            detail=(
                "A sessão não possui uma imagem "
                "armazenada."
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

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=(
                "O arquivo original da sessão "
                "não foi encontrado."
            ),
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        )

    try:
        registro = atualizar_caminho_normalizado(
            sessao_id=sessao_id,
            caminho_normalizado=(
                caminho_relativo_normalizado.as_posix()
            ),
        )

    except Exception:
        caminho_absoluto_normalizado.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "A imagem foi normalizada, mas não foi "
                "possível atualizar a sessão."
            ),
        )

    return {
        "sessao_id": registro["id"],
        "arquivo_original": caminho_original,
        "arquivo_normalizado": (
            registro["caminho_normalizado"]
        ),
        "normalizacao": resultado_normalizacao,
        "mensagem": (
            "Imagem normalizada para o padrão "
            "interno do VesteIA com sucesso."
        ),
    }