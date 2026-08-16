class SessaoProvador:
    """
    Representa uma sessão de experimentação do Provador VesteIA.

    A imagem não é armazenada dentro do PostgreSQL.
    O banco mantém apenas sua referência e seus metadados.
    """

    def __init__(
        self,
        produto_id: int,
        produto_nome: str,
        tamanho: str,
        modo: str,
        nome_arquivo: str,
        tipo_arquivo: str,
        tamanho_bytes: int,
        status: str,
        caminho_arquivo: str | None = None,
    ):
        self.produto_id = produto_id
        self.produto_nome = produto_nome
        self.tamanho = tamanho
        self.modo = modo

        self.nome_arquivo = nome_arquivo
        self.tipo_arquivo = tipo_arquivo
        self.tamanho_bytes = tamanho_bytes

        self.status = status
        self.caminho_arquivo = caminho_arquivo