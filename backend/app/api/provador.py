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
from app.perfil import perfil_usuario

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

from app.services.recomendacao_tamanho_provador import (
    gerar_recomendacao_tamanho_provador,
)

from app.services.deteccao_pessoa import (
    detectar_pessoa,
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
    produto_nome: str = Form(...),
    tamanho: str = Form(...),
    modo: str = Form("foto"),
):
    """
    Recebe, valida e registra
    uma nova sessão do provador.
    """

    if modo != "foto":
        raise HTTPException(
            status_code=400,
            detail=(
                "Este endpoint atualmente aceita "
                "apenas o modo foto."
            ),
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
        tamanho=tamanho,
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
            "id": produto_id,
            "nome": produto_nome,
            "tamanho": tamanho,
        },
        "arquivo": {
            "nome": foto.filename,
            "tipo": (
                foto.content_type
            ),
            "tamanho_bytes": (
                tamanho_arquivo
            ),
            "armazenado": True,
        },
        "mensagem": (
            "Sessão do Provador VesteIA "
            "registrada e imagem armazenada "
            "com sucesso."
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
    """
    Valida a sessão e inicia
    seu ciclo de processamento.
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
        "sessao_id": (
            resultado["id"]
        ),
        "status_anterior": (
            sessao["status"]
        ),
        "status_atual": (
            resultado["status"]
        ),
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
    """
    Finaliza com sucesso
    uma sessão em processamento.
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
        "sessao_id": (
            resultado["id"]
        ),
        "status_anterior": (
            sessao["status"]
        ),
        "status_atual": (
            resultado["status"]
        ),
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
    """
    Marca como erro
    uma sessão em processamento.
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
        "sessao_id": (
            resultado["id"]
        ),
        "status_anterior": (
            sessao["status"]
        ),
        "status_atual": (
            resultado["status"]
        ),
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
    """
    Analisa tecnicamente
    a imagem armazenada.
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
        "sessao_id": (
            sessao["id"]
        ),
        "produto": (
            sessao["produto_nome"]
        ),
        "status": (
            sessao["status"]
        ),
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
    """
    Cria uma versão JPEG/RGB
    padronizada da imagem.
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

    if not (
        caminho_absoluto_original
        .is_file()
    ):
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
        "sessao_id": (
            registro["id"]
        ),
        "arquivo_original": (
            caminho_original
        ),
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
    """
    Recupera e valida
    a imagem normalizada.
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
        "sessao_id": (
            sessao["id"]
        ),
        "produto": {
            "id": (
                sessao["produto_id"]
            ),
            "nome": (
                sessao["produto_nome"]
            ),
            "tamanho": (
                sessao["tamanho"]
            ),
        },
        "status_sessao": (
            sessao["status"]
        ),
        "entrada_visual": {
            "arquivo": (
                caminho_normalizado
            ),
            "origem": (
                "imagem_normalizada"
            ),
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
    """
    Avalia se a imagem normalizada
    possui qualidade suficiente.
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
        "sessao_id": (
            sessao["id"]
        ),
        "produto": {
            "id": (
                sessao["produto_id"]
            ),
            "nome": (
                sessao["produto_nome"]
            ),
            "tamanho": (
                sessao["tamanho"]
            ),
        },
        "avaliacao_foto": (
            avaliacao
        ),
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
    """
    Executa a detecção corporal
    e integra o resultado ao produto.

    A modelagem real do produto
    e a preferência de caimento
    são enviadas ao pipeline corporal.
    """

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

    # ======================================================
    # DETECÇÃO COM CONTEXTO DO PRODUTO
    # ======================================================

    try:
        deteccao = detectar_pessoa(
            caminho_absoluto,

            altura_cm=perfil_usuario.get(
                "altura_cm"
            ),

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

    contexto_corpo_produto = (
        gerar_contexto_corpo_produto(
            produto,
            deteccao,
        )
    )

    return {
        "sessao_id": (
            sessao["id"]
        ),

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

        "contexto_corpo_produto": (
            contexto_corpo_produto
        ),

        "mensagem": (
            "Detecção humana executada "
            "pelo pipeline visual do VesteIA "
            "com modelagem do produto, "
            "preferência de caimento "
            "e contexto corpo-produto integrados."
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

    Ordem principal:

    1. sessão;
    2. normalização;
    3. produto;
    4. detecção com contexto da peça;
    5. contexto corpo-produto;
    6. compatibilidade visual;
    7. compatibilidade dimensional;
    8. resultado dimensional;
    9. variações;
    10. recomendação experimental;
    11. decisão consolidada.
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

        if not (
            caminho_absoluto_original
            .is_file()
        ):
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
    #
    # IMPORTANTE:
    # O produto precisa ser carregado ANTES
    # da detecção para que sua modelagem seja
    # conhecida pelo pipeline corporal.
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
    # DETECÇÃO CORPORAL
    # ======================================================
    #
    # CORREÇÃO 1:
    #
    # A detecção recebe agora:
    # - altura do usuário;
    # - modelagem real da peça;
    # - preferência de caimento.
    #
    # Isso impede que uma peça Oversized
    # seja tratada internamente como Regular.
    # ======================================================

    try:
        deteccao = detectar_pessoa(
            caminho_absoluto,

            altura_cm=perfil_usuario.get(
                "altura_cm"
            ),

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
    # RECOMENDAÇÃO EXPERIMENTAL DE TAMANHO
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
    # RESPOSTA FINAL
    # ======================================================

    return {
        "sessao_id": (
            sessao_id
        ),

        "preferencia_caimento": (
            preferencia_caimento
        ),

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

        "deteccao_humana": (
            deteccao
        ),

        "mensagem": (
            "Pipeline automático do "
            "Provador VesteIA executado "
            "com análise corporal, modelagem "
            "real da peça, preferência de "
            "caimento, compatibilidade visual, "
            "compatibilidade dimensional, "
            "interpretação dimensional, "
            "comparação entre tamanhos "
            "e sugestão experimental "
            "personalizada preparados "
            "com sucesso."
        ),
    }