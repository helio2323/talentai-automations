import requests

response = requests.get("https://api.talentai.com.br/get_job_queue")
jobs = response.json()

for j in jobs:
    print(j)