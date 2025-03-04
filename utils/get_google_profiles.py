import time
import requests
import sys
import concurrent.futures  # Importando a biblioteca para execução paralela
sys.path.append('/home/helio/Documentos/talentai-automations')
from utils.google import get_linkedin_profile, get_candidates_from_google_linkedin
from aditionals_functions import get_job_queue

def process_job(job):
    try:
        query, navegador = get_linkedin_profile(
            cargos=[job["cargos"]],
            habilidades=[job["habilidades"]],
            ferramentas=[job["ferramentas"]],
            localizacoes=[job["localizacoes"]],
            max_interactions=[job["max_interactions"]],
            job_bubble_id=[job["job_bubble_id"]]
        )

        get_candidates_from_google_linkedin(navegador, job["job_bubble_id"], job["max_candidates"])

        # Chamar rota para atualizar o status da fila
        response = requests.post("https://api.talentai.com.br/update_job_status", json={"job_id": job["job_bubble_id"], "status": 1})

        print(f"Job {job['job_bubble_id']} processado com sucesso.")

    except Exception as e:
        print(f"Erro ao processar o job {job['job_bubble_id']}: {e}")

def get_pending_jobs():
    try:
        response = requests.get("https://api.talentai.com.br/get_job_queue")
        jobs = response.json()

        # Filtra jobs que ainda estão pendentes (assumindo que o status é 0 para pendente)
        pending_jobs = [job for job in jobs if job['status'] == 0]
        return pending_jobs
    except Exception as e:
        print(f"Erro ao obter jobs da fila: {e}")
        return []

def start_jobs():
    # Obtém os jobs pendentes
    pending_jobs = get_pending_jobs()

    # Enquanto houver jobs pendentes, processa até 5 de cada vez
    while pending_jobs:
        # Limite de 5 jobs simultâneos
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Processando até 5 jobs simultaneamente
            executor.map(process_job, pending_jobs[:5])  # Processa os 5 primeiros jobs pendentes

        # Após processar, verifica novamente os jobs pendentes
        pending_jobs = get_pending_jobs()

def monitor_jobs():
    while True:
        # Inicia o processo de monitoramento e processamento dos jobs
        start_jobs()

        # Aguardar um tempo antes de consultar novamente, para permitir que novos jobs sejam inseridos
        print("Aguardando novos jobs na fila...")
        time.sleep(5)  # Reduzi o tempo de espera para 5 segundos para uma verificação mais constante

if __name__ == "__main__":
    monitor_jobs()
