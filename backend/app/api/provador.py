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


@router.post("/preparar")
async def preparar_experiencia(
    foto: UploadFile = File(...),
    produto_id: int = Form(...),
    produto_nome: str = Form(...),
    tamanho: str = Form(...),
    modo: str = Form("foto"),
):
    """
    Recebe uma sessão do Provador VesteIA,
    valida a imagem e registra seus metadados no PostgreSQL.
    """

    if modo != "foto":
        raise HTTPException(
            status_code=400,
            detail="Este endpoint atualmente aceita apenas o modo foto.",
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

    await foto.seek(0)

    sessao = SessaoProvador(
        produto_id=produto_id,
        produto_nome=produto_nome,
        tamanho=tamanho,
        modo=modo,
        nome_arquivo=foto.filename,
        tipo_arquivo=foto.content_type,
        tamanho_bytes=tamanho_arquivo,
        status="pronto_para_processar",
    )

    try:
        registro = adicionar_sessao_provador(sessao)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível registrar a sessão no PostgreSQL.",
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
        },
        "mensagem": (
            "Sessão do Provador VesteIA registrada "
            "no PostgreSQL com sucesso."
        ),
    }


@router.get("/sessoes")
def listar_sessoes():
    """
    Lista as sessões já registradas pelo Provador VesteIA.
    """

    try:
        return listar_sessoes_provador()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar as sessões do provador.",
        )