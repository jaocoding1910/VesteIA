from pathlib import Path

from PIL import (
    Image,
    ImageOps,
    UnidentifiedImageError,
)


FORMATOS_SUPORTADOS = {
    "JPEG",
    "PNG",
    "WEBP",
}


LARGURA_MINIMA = 512
ALTURA_MINIMA = 512


def analisar_imagem(caminho_arquivo):
    """
    Abre uma imagem armazenada pelo Provador VesteIA
    e retorna informações técnicas reais do arquivo.
    """

    caminho = Path(caminho_arquivo)

    if not caminho.is_file():
        raise FileNotFoundError(
            "Arquivo da sessão não encontrado."
        )

    try:
        with Image.open(caminho) as imagem:
            imagem.load()

            largura, altura = imagem.size

            formato = imagem.format
            modo_cor = imagem.mode

    except UnidentifiedImageError as erro:
        raise ValueError(
            "O arquivo armazenado não é uma imagem válida."
        ) from erro

    except OSError as erro:
        raise ValueError(
            "Não foi possível ler a imagem armazenada."
        ) from erro

    total_pixels = largura * altura

    return {
        "largura_px": largura,
        "altura_px": altura,
        "formato_real": formato,
        "modo_cor": modo_cor,
        "total_pixels": total_pixels,
        "imagem_valida": True,
    }


def normalizar_imagem(
    caminho_origem,
    caminho_destino,
):
    """
    Converte uma imagem suportada para o padrão interno
    do VesteIA: JPEG + RGB.

    Também corrige orientação EXIF e trata transparência.
    """

    origem = Path(caminho_origem)
    destino = Path(caminho_destino)

    if not origem.is_file():
        raise FileNotFoundError(
            "Arquivo original não encontrado."
        )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with Image.open(origem) as imagem:
            formato_original = imagem.format

            if formato_original not in FORMATOS_SUPORTADOS:
                raise ValueError(
                    "Formato de imagem não suportado "
                    "pelo normalizador do VesteIA."
                )

            imagem_corrigida = ImageOps.exif_transpose(
                imagem
            )

            largura_original, altura_original = (
                imagem_corrigida.size
            )

            if (
                imagem_corrigida.mode in ("RGBA", "LA")
                or (
                    imagem_corrigida.mode == "P"
                    and "transparency"
                    in imagem_corrigida.info
                )
            ):
                imagem_rgba = imagem_corrigida.convert(
                    "RGBA"
                )

                fundo = Image.new(
                    "RGB",
                    imagem_rgba.size,
                    (255, 255, 255),
                )

                fundo.paste(
                    imagem_rgba,
                    mask=imagem_rgba.getchannel("A"),
                )

                imagem_rgb = fundo

            else:
                imagem_rgb = imagem_corrigida.convert(
                    "RGB"
                )

            imagem_rgb.save(
                destino,
                format="JPEG",
                quality=92,
                optimize=True,
            )

            largura_final, altura_final = (
                imagem_rgb.size
            )

    except UnidentifiedImageError as erro:
        raise ValueError(
            "O arquivo não contém uma imagem válida."
        ) from erro

    except OSError as erro:
        raise ValueError(
            "Não foi possível normalizar a imagem."
        ) from erro

    return {
        "formato_origem": formato_original,
        "formato_saida": "JPEG",
        "modo_saida": "RGB",
        "largura_original_px": largura_original,
        "altura_original_px": altura_original,
        "largura_final_px": largura_final,
        "altura_final_px": altura_final,
        "tamanho_normalizado_bytes": destino.stat().st_size,
        "normalizada": True,
    }


def avaliar_entrada_visual(caminho_normalizado):
    """
    Avalia tecnicamente a imagem normalizada que será
    utilizada como entrada oficial do pipeline visual.

    Esta função ainda não detecta pessoa, corpo ou pose.
    """

    caminho = Path(caminho_normalizado)

    if not caminho.is_file():
        raise FileNotFoundError(
            "Imagem normalizada não encontrada."
        )

    try:
        with Image.open(caminho) as imagem:
            imagem.load()

            largura, altura = imagem.size
            formato = imagem.format
            modo_cor = imagem.mode

    except UnidentifiedImageError as erro:
        raise ValueError(
            "A imagem normalizada não é válida."
        ) from erro

    except OSError as erro:
        raise ValueError(
            "Não foi possível ler a imagem normalizada."
        ) from erro

    total_pixels = largura * altura

    proporcao = round(
        largura / altura,
        3,
    )

    if altura > largura:
        orientacao = "retrato"
    elif largura > altura:
        orientacao = "paisagem"
    else:
        orientacao = "quadrada"

    resolucao_suficiente = (
        largura >= LARGURA_MINIMA
        and altura >= ALTURA_MINIMA
    )

    formato_padrao = (
        formato == "JPEG"
    )

    modo_padrao = (
        modo_cor == "RGB"
    )

    entrada_pronta = (
        resolucao_suficiente
        and formato_padrao
        and modo_padrao
    )

    observacoes = []

    if not resolucao_suficiente:
        observacoes.append(
            "resolução abaixo do mínimo recomendado"
        )

    if not formato_padrao:
        observacoes.append(
            "imagem fora do formato interno JPEG"
        )

    if not modo_padrao:
        observacoes.append(
            "imagem fora do modo interno RGB"
        )

    if not observacoes:
        observacoes.append(
            "imagem tecnicamente pronta para o pipeline visual"
        )

    return {
        "largura_px": largura,
        "altura_px": altura,
        "total_pixels": total_pixels,
        "proporcao": proporcao,
        "orientacao": orientacao,
        "formato": formato,
        "modo_cor": modo_cor,
        "resolucao_suficiente": resolucao_suficiente,
        "formato_padrao": formato_padrao,
        "modo_padrao": modo_padrao,
        "entrada_pronta": entrada_pronta,
        "observacoes": observacoes,
    }