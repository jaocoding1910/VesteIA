import os

import psycopg2
from dotenv import load_dotenv


# Carrega as variáveis definidas no arquivo .env.
load_dotenv()


def conectar():
    """
    Cria e retorna uma conexão com o PostgreSQL
    utilizando variáveis de ambiente.
    """

    conexao = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    return conexao