from app.database.database import conectar


def _garantir_tabela_sessoes(cursor):
    """
    Garante a existência e a estrutura da tabela
    utilizada pelo Provador VesteIA.
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
            caminho_arquivo TEXT,
            caminho_normalizado TEXT,
            criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        ALTER TABLE sessoes_provador
        ADD COLUMN IF NOT EXISTS caminho_arquivo TEXT
        """
    )

    cursor.execute(
        """
        ALTER TABLE sessoes_provador
        ADD COLUMN IF NOT EXISTS caminho_normalizado TEXT
        """
    )


def _converter_linha_para_sessao(linha):
    """
    Converte uma linha retornada pelo PostgreSQL
    em um dicionário padronizado de sessão.
    """

    return {
        "id": linha[0],
        "produto_id": linha[1],
        "produto_nome": linha[2],
        "tamanho": linha[3],
        "modo": linha[4],
        "nome_arquivo": linha[5],
        "tipo_arquivo": linha[6],
        "tamanho_bytes": linha[7],
        "status": linha[8],
        "caminho_arquivo": linha[9],
        "caminho_normalizado": linha[10],
        "criado_em": linha[11],
    }


def adicionar_sessao_provador(sessao):
    """
    Registra uma nova sessão do Provador VesteIA.
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
                status,
                caminho_arquivo,
                caminho_normalizado
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING
                id,
                criado_em
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
                sessao.caminho_arquivo,
                sessao.caminho_normalizado,
            ),
        )

        resultado = cursor.fetchone()

        conexao.commit()

        return {
            "id": resultado[0],
            "criado_em": resultado[1],
            "status": sessao.status,
            "caminho_arquivo": sessao.caminho_arquivo,
            "caminho_normalizado": (
                sessao.caminho_normalizado
            ),
        }

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


def listar_sessoes_provador():
    """
    Retorna todas as sessões registradas.
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
                caminho_arquivo,
                caminho_normalizado,
                criado_em
            FROM sessoes_provador
            ORDER BY id DESC
            """
        )

        resultados = cursor.fetchall()

        conexao.commit()

        return [
            _converter_linha_para_sessao(linha)
            for linha in resultados
        ]

    finally:
        cursor.close()
        conexao.close()


def buscar_sessao_provador_por_id(sessao_id):
    """
    Busca uma sessão específica pelo ID.
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
                caminho_arquivo,
                caminho_normalizado,
                criado_em
            FROM sessoes_provador
            WHERE id = %s
            """,
            (sessao_id,),
        )

        resultado = cursor.fetchone()

        conexao.commit()

        if resultado is None:
            return None

        return _converter_linha_para_sessao(
            resultado
        )

    finally:
        cursor.close()
        conexao.close()


def atualizar_status_sessao(
    sessao_id,
    novo_status,
):
    """
    Atualiza o status de uma sessão.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """
            UPDATE sessoes_provador
            SET status = %s
            WHERE id = %s
            RETURNING id, status
            """,
            (
                novo_status,
                sessao_id,
            ),
        )

        resultado = cursor.fetchone()

        if resultado is None:
            conexao.rollback()
            return None

        conexao.commit()

        return {
            "id": resultado[0],
            "status": resultado[1],
        }

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


def atualizar_caminho_normalizado(
    sessao_id,
    caminho_normalizado,
):
    """
    Registra no PostgreSQL o caminho da imagem
    normalizada de uma sessão.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """
            UPDATE sessoes_provador
            SET caminho_normalizado = %s
            WHERE id = %s
            RETURNING
                id,
                caminho_normalizado
            """,
            (
                caminho_normalizado,
                sessao_id,
            ),
        )

        resultado = cursor.fetchone()

        if resultado is None:
            conexao.rollback()
            return None

        conexao.commit()

        return {
            "id": resultado[0],
            "caminho_normalizado": resultado[1],
        }

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()