import sqlite3
import os

# Caminho absoluto para evitar erros
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Sobe um nível para a pasta raiz
DB_PATH = os.path.join(BASE_DIR, 'utils', 'profiles.db')

def get_db_connection():
    """Cria uma conexão com o banco de dados na pasta utils."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_table_queue():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            max_candidates INTEGER DEFAULT 10,
            status INTEGER DEFAULT 0,  -- 0 = Pendente, 1 = Concluído
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cargos TEXT,  -- Lista de cargos
            habilidades TEXT,  -- Lista de habilidades
            ferramentas TEXT,  -- Lista de ferramentas
            localizacoes TEXT,  -- Lista de localizações
            max_interactions INTEGER DEFAULT 5,
            job_bubble_id TEXT
        )
    ''')
    conn.commit()
    conn.close()


import json

def insert_job_queue(job_id, status=0, max_candidates=10, cargos=None, habilidades=None, ferramentas=None, localizacoes=None, max_interactions=5, job_bubble_id=None):
    if cargos is None:
        cargos = []
    if habilidades is None:
        habilidades = []
    if ferramentas is None:
        ferramentas = []
    if localizacoes is None:
        localizacoes = []
    
    # Converte listas para string JSON
    cargos_json = json.dumps(cargos)
    habilidades_json = json.dumps(habilidades)
    ferramentas_json = json.dumps(ferramentas)
    localizacoes_json = json.dumps(localizacoes)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO queue (job_id, status, max_candidates, cargos, habilidades, ferramentas, localizacoes, max_interactions, job_bubble_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_id, status, max_candidates, cargos_json, habilidades_json, ferramentas_json, localizacoes_json, max_interactions, job_bubble_id))
    conn.commit()
    job_inserted_id = cursor.lastrowid
    conn.close()
    return job_inserted_id


import json

def get_job_queue():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM queue WHERE status = 0 ORDER BY timestamp ASC LIMIT 1
    ''')
    
    job = cursor.fetchone()
    colunas = [desc[0] for desc in cursor.description]

    conn.close()

    if job is None:
        return {"message": "No pending jobs"}

    job_dict = dict(zip(colunas, job))

    return job_dict  # Retorna um dicionário, não uma string JSON



# Atualiza o status de um job (0 = Pendente, 1 = Concluído)
def update_job_status(job_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE queue SET status = ? WHERE job_id = ?
    ''', (status, job_id))
    conn.commit()
    conn.close()

create_table_queue()
