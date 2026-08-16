from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.sessao_provador import SessaoProvador
from app.services.provador import (
    adicionar_sessao_provador,
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


# Caminho da pasta backend/.
BACKEND_DIR = Path(__file__).resolve().parents[2]

# Local onde as fotos serão armazenadas no MVP.
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

    O nome original enviado pelo usuário não é utilizado
    como nome físico do arquivo.
    """

    PASTA_UPLOADS_PROVADOR.mkdir(
        parents=True,
        exist_ok=True,
    )

    extensao = EXTENSOES_IMAGEM[tipo_arquivo]

    nome_interno = (
        f"{uuid4().hex}{extensao}"
    )

    caminho_absoluto = (
        PASTA_UPLOADS_PROVADOR
        / nome_interno
    )

    caminho_absoluto.write_bytes(conteudo)

    caminho_relativo = (
        Path("uploads")
        / "provador"
        / nome_interno
    )

    return (
        caminho_relativo.as_posix(),
        caminho_absoluto,
    )


@router.post("/preparar")
async def preparar_experiencia(
    foto: UploadFile = File(...),
    produto_id: int = Form(...),
    produto_nome: str = Form(...),
    tamanho: str = Form(...),
    modo: str = Form("foto"),
):
    """
    Recebe a sessão do Provador VesteIA.

    A imagem é validada, armazenada localmente e
    sua referência é registrada no PostgreSQL.
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

    tamanho_arquivo = len(conteudo_foto)

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
        # Evita deixar uma imagem órfã caso
        # o registro no PostgreSQL falhe.
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

        "status_processamento": (
            registro["status"]
        ),

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
    Lista as sessões registradas pelo Provador VesteIA.
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