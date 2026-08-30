class SessaoProvador:
    """
    Representa uma sessão de experimentação do Provador VesteIA.

    A imagem original e sua versão normalizada ficam
    armazenadas fora do PostgreSQL.
    O banco mantém apenas suas referências.

    O tamanho pode ser desconhecido no início da sessão.
    No fluxo foto-first, o tamanho é determinado
    posteriormente pelo motor do Provador.
    """

    def __init__(
        self,
        produto_id: int,
        produto_nome: str,
        modo: str,
        nome_arquivo: str,
        tipo_arquivo: str,
        tamanho_bytes: int,
        status: str,
        tamanho: str | None = None,
        caminho_arquivo: str | None = None,
        caminho_normalizado: str | None = None,
    ):
        self.produto_id = produto_id
        self.produto_nome = produto_nome

        # No novo fluxo foto-first,
        # a sessão pode nascer sem tamanho definido.
        self.tamanho = tamanho

        self.modo = modo

        self.nome_arquivo = nome_arquivo
        self.tipo_arquivo = tipo_arquivo
        self.tamanho_bytes = tamanho_bytes

        self.status = status

        self.caminho_arquivo = caminho_arquivo
        self.caminho_normalizado = caminho_normalizado