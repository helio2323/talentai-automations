import time
import requests
import sys
sys.path.append('/home/helio/Documentos/talentai-automations')


jobs = requests.get("https://api.talentai.com.br/get_job_queue")
j =  jobs.json()

print(j["job_bubble_id"])