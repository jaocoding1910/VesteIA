import psycopg2

def conectar():
    conexao = psycopg2.connect(
        host="localhost",
        database="vesteia",
        user="postgres",
        password="J48528742j@"
    )

    return conexao