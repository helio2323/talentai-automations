from crewai import Agent, Crew, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, FileReadTool, PDFSearchTool
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import json
import re
from pydantic import BaseModel, ValidationError
from llama_functions import llm_parse

load_dotenv()

# =======================
# MODELOS Pydantic
# =======================
class Address(BaseModel):
    street: str
    city: str
    state: str
    country: str
    zip_code: str

class Contact(BaseModel):
    phone: str
    email: str
    website: str
    address: list[Address]

class About(BaseModel):
    name: str
    position: str
    contact: Contact
    professional_objective: str

class Experience(BaseModel):
    titulo: str
    years: str
    institution: str
    description: str
    actual_position: str
    start_date: str
    end_date: str

class Education(BaseModel):
    diploma: str
    years: str
    institution: str
    description: str
    current: str
    start_date: str
    end_date: str
    city: str
    degree: str

class AdditionalCourse(BaseModel):
    course: str
    institution: str
    notes: str
    years: str
    start_date: str
    end_date: str

class Curriculo(BaseModel):
    about: About
    experience: list[Experience]
    education: list[Education]
    skills: list[str]
    languages: list
    additional_courses: list[AdditionalCourse]

class CurriculoModel(BaseModel):
    curriculos: list[Curriculo]

# Exemplo de JSON esperado (para referência na tarefa do agente)
json_example = """
{
    "curriculos": [
        {
            "about": {
                "name": "Nome do dono do currículo",
                "position": "Profissão",
                "contact": {
                    "phone": "Telefone",
                    "email": "Email",
                    "website": "Website (caso tenha)",
                    "address": [
                        {
                            "street": "Logradouro",
                            "city": "Cidade",
                            "state": "Estado",
                            "country": "País",
                            "zip_code": "CEP"
                        }
                    ]
                },
                "professional_objective": "Objetivo profissional (caso tenha)"
            },
            "experience": [
                {
                    "titulo": "Nome do cargo",
                    "years": "Data de início - Data de término",
                    "institution": "Nome da empresa",
                    "description": "Descrição (caso tenha)",
                    "actual_position": "yes",
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-30"
                }
            ],
            "education": [
                {
                    "diploma": "Nome do curso",
                    "years": "Data de início - Data de término",
                    "institution": "Nome da instituição",
                    "description": "Descrição (caso tenha)",
                    "current": "yes",
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-30",
                    "city": "Guarulhos",
                    "degree": "Bacharelado or Técnico"
                }
            ],
            "skills": ["Habilidade 1", "Habilidade 2", "Habilidade 3"],
            "languages": [],
            "additional_courses": [
                {
                    "course": "Python",
                    "institution": "OneBitCode",
                    "notes": "",
                    "years": "2023",
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-30"
                },
                {
                    "course": "VueJs",
                    "institution": "OneBitCode",
                    "notes": "",
                    "years": "2023",
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-30"
                }
            ]
        }
    ]
}
"""

# =======================
# FUNÇÃO DE CONVERSÃO
# =======================
def convert_pdf_to_json(pdf_file_path: str) -> dict:
    """
    Converte um arquivo PDF de currículo em JSON estruturado (tipo dict).
    O arquivo PDF deve ser passado como argumento 'pdf_file_path'.
    """
    API_KEY = os.getenv("OP_AI_KEY")
    llm = LLM(model="gpt-4o-mini", temperature=0.5, api_key=API_KEY)

    # Lê o conteúdo do PDF
    reader = PdfReader(pdf_file_path)
    texto = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texto += page_text + "\n"

    # =======================
    # CONFIGURAÇÃO DO AGENTE
    # =======================
    Leitor = Agent(
        role="Leitor de curriculo",
        goal="""Seu objetivo é carregar os dados do currículo que serão passados para o JSON. 
Os dados precisam ser exatamente os mesmos que estão no PDF.""",
        backstory="Você é um leitor de dados com vasta experiência em extrair informações de currículos e estruturá-los em JSON.",
        verbose=True,
        llm=llm,
    )

    carregar_curriculo = Task(
        description=f"""
Os dados devem ser carregados do seguinte texto extraído do PDF:
{texto}

Aja como um especialista em análise de currículos para extrair os dados estruturados no formato JSON.
Sua tarefa é processar o texto, identificar as informações conforme a estrutura definida abaixo,
e retornar exclusivamente um objeto JSON conforme o exemplo fornecido, sem nenhum texto adicional.

Instruções:
- O JSON deve conter os campos: about, experience, education, skills, languages, additional_courses.
- Se alguma informação não estiver disponível, mantenha a chave com valor "" ou uma lista vazia.
- Não adicione informações não presentes no currículo.
- Não repita chaves no JSON.
- em degree utilize o valor "Bacharelado" ou "Técnico" nao utilize outro valor

Exemplo de JSON esperado:
{json_example}
""",
        agent=Leitor,
        expected_output="JSON",
        llm=llm,
        verbose=True
    )

    crew = Crew(
        name="Curriculo",
        description="Processamento de currículo em PDF",
        tasks=[carregar_curriculo],
        llm=llm,
        verbose=True,
        agents=[Leitor],
        expected_output="JSON",
        json_dict=True,
    )

    crew_output = crew.kickoff()
    json_formatted = crew_output.raw.strip()

    # Remove aspas extras e backticks (se existirem)
    if json_formatted.startswith('"') and json_formatted.endswith('"'):
        json_formatted = json_formatted[1:-1]
    json_formatted = json_formatted.replace("```", "")

    # Converte a string para um dicionário
    try:
        data = json.loads(json_formatted)
    except json.JSONDecodeError as e:
        print("Erro ao decodificar o JSON:", e)
        data = {}

    # Validação com Pydantic
    try:
        curriculo_model = CurriculoModel(**data)
    except ValidationError as ve:
        print("Erro na validação do JSON com Pydantic:", ve)
        return {}

    # Retorna o dicionário validado para iteração posterior
    return curriculo_model.dict()

# =======================
# EXECUÇÃO
# =======================
if __name__ == '__main__':
    # Informe o caminho do arquivo PDF que o agente deverá ler:
    pdf_path = "caminho/para/seu/arquivo.pdf"  # Substitua pelo caminho real do seu PDF
    curriculo_dict = convert_pdf_to_json(pdf_path)
    
    # Exemplo de iteração sobre o dicionário retornado
    if curriculo_dict:
        for curriculo in curriculo_dict.get("curriculos", []):
            about = curriculo.get("about", {})
            print("Nome:", about.get("name"))
            print("Cargo:", about.get("position"))
            print("Objetivo Profissional:", about.get("professional_objective"))
            print("\nExperiências:")
            for exp in curriculo.get("experience", []):
                print("  Título:", exp.get("titulo"))
                print("  Instituição:", exp.get("institution"))
                print("  Descrição:", exp.get("description"))
                print("-" * 40)
