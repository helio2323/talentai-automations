from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, FileReadTool, PDFSearchTool
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
import os
import contextlib
import warnings
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests

load_dotenv()

def load_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Carregando os dados dos arquivos
candidate_cv_info = load_file_content('candidate_info.txt')
job_info = load_file_content('job_info.txt')

API_KEY = os.getenv("OP_AI_KEY")
os.environ["OPENAI_API_KEY"] = "NA"

gpt = LLM(model="gpt-4o-mini", temperature=0.5, api_key=API_KEY)

ollama = LLM(
    model="ollama/llama3.1",  # Especificando o provedor
    base_url="http://localhost:11434",
    temperature=0.5
)
GROQ_API_KEY="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"

groq = LLM(
    model="groq/llama-3.1-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.5
)

def create_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

selected_llm = gpt

json_schema = """
{
  "score": "Pontuação de 0 a 100, indicando a aderência do candidato aos requisitos da vaga",
  "strengths": "Lista detalhada de pontos fortes do candidato em relação aos requisitos da vaga",
  "weaknesses": "Lista de lacunas ou áreas onde o candidato não atende aos requisitos da vaga",
  "alignment": {
    "hard_skills": "Nível de alinhamento das hard skills do candidato com os requisitos obrigatórios e desejáveis",
    "soft_skills": "Nível de alinhamento das soft skills do candidato com os requisitos comportamentais da vaga"
  },
  "missing_information": "Quaisquer informações ausentes em {candidate_cv_info} ou {job_info} que dificultaram a avaliação",
  "justification": "Resumo textual que explica o score atribuído com base nos requisitos da vaga e qualificações do candidato",
  "recommendation": "Recomendação final, categorizada como 'Altamente recomendável', 'Recomendável com reservas' ou 'Não recomendável'"
}

"""

Recrutador = Agent(
    role="Recrutador",
    goal="Avaliar o currículo do candidato e o perfil do cargo para determinar se o candidato é adequado para o cargo",
    backstory="Você é um recrutador experiente e sempre busca avaliar o currículo do candidato e o perfil do cargo para determinar se o candidato é adequado para o cargo",
    verbose=True,
    allow_delegation=False,
    llm=selected_llm
)

Avaliar_candidato = Task(
    description=f"""Aja como um especialista em Recursos Humanos e recrutamento com experiência em avaliação de candidatos para diferentes tipos de vagas. Sua tarefa é realizar uma análise objetiva e detalhada, comparando as qualificações e habilidades do candidato com os requisitos da vaga, considerando os seguintes aspectos:

Hard skills: Experiências profissionais, formações acadêmicas, certificações e competências técnicas exigidas pela vaga.
Soft skills: Competências comportamentais e interpessoais relevantes, como comunicação, trabalho em equipe, resolução de problemas e liderança.
Aderência geral: Compatibilidade com os requisitos obrigatórios e desejáveis descritos na vaga.
Dados Fornecidos:
{candidate_cv_info}: Informações sobre o candidato, incluindo experiências profissionais, habilidades, formações e outras qualificações.
{job_info}: Detalhes da vaga, incluindo requisitos obrigatórios, desejáveis, responsabilidades e competências esperadas.
Suas Tarefas:
Comparar: Avalie as informações do candidato com os requisitos obrigatórios e desejáveis da vaga, identificando lacunas e alinhamentos.
Classificar: Atribua um score de 0 a 100, indicando o grau de aderência do candidato à vaga.
Priorizar: Dê preferência a candidatos que atendam aos requisitos obrigatórios e demonstrem diferenciais significativos.
Relatar Dados Faltantes: Se informações cruciais estiverem ausentes em {candidate_cv_info} ou {job_info}, mencione isso no output.
Formato da Resposta:
Sua avaliação deve ser concisa e apresentada no seguinte formato JSON:

{json_schema}


Orientações Adicionais:
Para cada hard skill, avalie seu nível de aderência como 'Totalmente atendido', 'Parcialmente atendido' ou 'Não atendido'.
Para cada soft skill, avalie seu impacto potencial na execução das responsabilidades da vaga.
Se o candidato apresentar diferenciais que superem algumas lacunas, destaque isso no campo strengths.
Caso os dados da vaga ou do candidato estejam mal estruturados, identifique as inconsistências e forneça uma análise baseada nas informações disponíveis.
""",
    expected_output="JSON",
    agent=Recrutador,
    llm=selected_llm,
)

crew = Crew(
    name="Avaliar candidato",
    description="Avaliar o candidato para o cargo",
    tasks=[Avaliar_candidato],
    agents=[Recrutador],
    llm=selected_llm,
    verbose=True
)

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ResourceWarning)
        with contextlib.closing(crew):
            crew_output = crew.kickoff()
    print(crew_output.raw)
except Exception as e:
    print(f"Erro durante a execução: {e}")