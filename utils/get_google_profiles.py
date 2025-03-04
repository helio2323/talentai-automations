import time
import requests
import sys
sys.path.append('/home/helio/Documentos/talentai-automations')
from utils.google import get_linkedin_profile, get_candidates_from_google_linkedin

from aditionals_functions import get_job_queue

while True:

    time.sleep(5)
    
    try:
    
        response = requests.get("https://api.talentai.com.br/get_job_queue")
        jobs = response.json()
        
        query, navegador = get_linkedin_profile(
            cargos=[jobs["cargos"]],
            habilidades=[jobs["habilidades"]],
            ferramentas=[jobs["ferramentas"]],
            localizacoes=[jobs["localizacoes"]],
            max_interactions=[jobs["max_interactions"]],
            job_bubble_id=[jobs["job_bubble_id"]]
        )

        get_candidates_from_google_linkedin(navegador, jobs["job_bubble_id"], jobs["max_candidates"])

        #chamar rota para atualizar o status da fila
        response = requests.post("https://api.talentai.com.br/update_job_status", json={"job_id": jobs["job_bubble_id"], "status": 1})
        

    except Exception as e:
        print(f"Erro ao obter jobs da fila: {e}")
        continue
