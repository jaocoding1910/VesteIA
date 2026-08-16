from pathlib import Path

from PIL import Image, UnidentifiedImageError


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
            # Carrega os pixels para validar o arquivo de verdade.
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