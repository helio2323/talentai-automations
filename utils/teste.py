import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Sobe um nível para a pasta raiz
DB_PATH = os.path.join(BASE_DIR, 'utils', 'profiles.db')
DBPATH_LOGS = os.path.join(BASE_DIR, 'utils', 'logs.db')

def limpar_banco_de_dados(nome_arquivo_db=DBPATH_LOGS):
    """
    Remove todos os registros de todas as tabelas no banco de dados SQLite.

    :param nome_arquivo_db: Nome do arquivo do banco de dados SQLite.
    """
    # Conexão com o banco de dados
    conn = sqlite3.connect(nome_arquivo_db)
    cursor = conn.cursor()

    # Obter todas as tabelas do banco de dados
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()

    if not tabelas:
        print("Nenhuma tabela encontrada no banco de dados.")
    else:
        for tabela in tabelas:
            nome_tabela = tabela[0]
            # Limpar a tabela
            cursor.execute(f"DELETE FROM {nome_tabela};")
            print(f"Tabela '{nome_tabela}' limpa com sucesso.")

        # Confirmar alterações
        conn.commit()

    # Fechar a conexão
    conn.close()
    print(f"Banco de dados '{nome_arquivo_db}' foi completamente limpo.")

limpar_banco_de_dados()