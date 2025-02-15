import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.aditionals_functions import get_job_queue, update_job_status   
from utils.google import search_profiles
import time

def execute_job_function(job_data):
    # Aqui, você chama a função `search_profiles` com os dados do job
    result = search_profiles(
        cargos=job_data.get("cargos", []),
        habilidades=job_data.get("habilidades", []),
        ferramentas=job_data.get("ferramentas", []),
        localizacoes=job_data.get("localizacoes", []),
        max_interactions=job_data.get("max_interactions", 10),
        job_bubble_id=job_data.get("job_bubble_id", '')
    )
    print(f"Resultado da execução: {result}")
# Função que verifica a cada 5 segundos se há um job pendente
def check_and_execute_job():
    while True:
        job = get_job_queue()

        if job:  # Se encontrar um job pendente
            job_id = job[1]  # job_id está na segunda posição da tupla
            print(f"Job {job_id} encontrado e está Pendente.")
            
            # Verifica se os dados do job são strings e converte se necessário
            job_data = {
                "job_id": job[1],
                "cargos": str(job[5]).split(',') if isinstance(job[2], str) else [job[5]],
                "habilidades": str(job[6]).split(',') if isinstance(job[6], str) else [job[6]],
                "ferramentas": str(job[7]).split(',') if isinstance(job[7], str) else [job[7]],
                "localizacoes": str(job[8]).split(',') if isinstance(job[8], str) else [job[8]],
                "max_interactions": job[9],
                "job_bubble_id": job[10]
            }

            print(job_data)

            # Executa a função para o job com os dados
            execute_job_function(job_data)

            # Após a execução, atualiza o status para Concluído
            update_job_status(job_id, 1)
            print(f"Job {job_id} concluído e status atualizado para 1.")

        else:
            print("Nenhum job pendente encontrado. Aguardando...")

        # Espera 5 segundos antes de verificar novamente
        time.sleep(5)


# Chama a função para começar a verificação
check_and_execute_job()
