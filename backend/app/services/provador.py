from app.database.database import conectar


def _garantir_tabela_sessoes(cursor):
    """
    Garante a existência da tabela utilizada
    para registrar as sessões do Provador VesteIA.
    """

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessoes_provador (
            id BIGSERIAL PRIMARY KEY,
            produto_id BIGINT NOT NULL,
            produto_nome TEXT NOT NULL,
            tamanho VARCHAR(10) NOT NULL,
            modo VARCHAR(20) NOT NULL,
            nome_arquivo TEXT NOT NULL,
            tipo_arquivo VARCHAR(100) NOT NULL,
            tamanho_bytes BIGINT NOT NULL,
            status VARCHAR(50) NOT NULL,
            criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def adicionar_sessao_provador(sessao):
    """
    Registra uma nova sessão do Provador VesteIA
    no PostgreSQL e retorna o ID criado pelo banco.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        _garantir_tabela_sessoes(cursor)

        cursor.execute(
            """
            INSERT INTO sessoes_provador (
                produto_id,
                produto_nome,
                tamanho,
                modo,
                nome_arquivo,
                tipo_arquivo,
                tamanho_bytes,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, criado_em
            """,
            (
                sessao.produto_id,
                sessao.produto_nome,
                sessao.tamanho,
                sessao.modo,
                sessao.nome_arquivo,
                sessao.tipo_arquivo,
                sessao.tamanho_bytes,
                sessao.status,
            ),
        )

        resultado = cursor.fetchone()

        conexao.commit()

        return {
            "id": resultado[0],
            "criado_em": resultado[1],
            "status": sessao.status,
        }

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


def listar_sessoes_provador():
    """
    Retorna as sessões registradas no PostgreSQL,
    começando pela mais recente.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        _garantir_tabela_sessoes(cursor)

        cursor.execute(
            """
            SELECT
                id,
                produto_id,
                produto_nome,
                tamanho,
                modo,
                nome_arquivo,
                tipo_arquivo,
                tamanho_bytes,
                status,
                criado_em
            FROM sessoes_provador
            ORDER BY id DESC
            """
        )

        resultados = cursor.fetchall()

        conexao.commit()

        sessoes = []

        for linha in resultados:
            sessoes.append(
                {
                    "id": linha[0],
                    "produto_id": linha[1],
                    "produto_nome": linha[2],
                    "tamanho": linha[3],
                    "modo": linha[4],
                    "nome_arquivo": linha[5],
                    "tipo_arquivo": linha[6],
                    "tamanho_bytes": linha[7],
                    "status": linha[8],
                    "criado_em": linha[9],
                }
            )

        return sessoes

    finally:
        cursor.close()
        conexao.close()