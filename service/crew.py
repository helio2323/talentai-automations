from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, FileReadTool, PDFSearchTool
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import json
import re


load_dotenv()

import json

def convert_pdf_to_json(file):

  API_KEY=os.getenv("OP_AI_KEY")

  llm = LLM(model="gpt-4o-mini", temperature=0.5,
            api_key=API_KEY)

  reader = PdfReader(file)
  texto = ""

  for page in reader.pages:
      texto += page.extract_text()

  json_example = """
  {
    "curriculos": [
      {{
        "about": {{
          "name": "Nome do dono do currículo",
          "position": "Profissão",
          "contact": {{
            "phone": "Telefone",
            "email": "Email",
            "website": "Website (caso tenha)",
            "address": [{{
              "street": "Logradouro",
              "city": "Cidade",
              "state": "Estado",
              "country": "País",
              "zip_code": "CEP"}}
            ]
          }},
          "professional_objective": "Objetivo profissional (caso tenha)"
        }},
        "experience": [
          {{
            "certification_name": "Nome do cargo",
            "years": "Data de início - Data de término",
            "institution": "Nome da empresa",
            "description": "Descrição (caso tenha)",
            "actual_position": "yes",
            "start_date": "2023-01-01",
            "end_date": "2023-06-30",
          }}
        ],
        "education": [
          {{
            "diploma": "Nome do curso",
            "years": "Data de início - Data de término",
            "institution": "Nome da instituição",
            "description": "Descrição (caso tenha)",
            "current": "yes",
            "start_date": "2023-01-01",
            "end_date": "2023-06-30",
            "city": "Guarulhos",
            "degree" : "Bacharelado or Tecnico"
          }}
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
                  },]
      }}
    ]
  }"""

  """Criar os agentes que vao carregar o curriculo e passar os dados para o formato JSON"""

  Leitor = Agent(
      role="Leitor de curriculo",
      goal="""Seu objetivo é carregar os dados do curriculo que serao passados para o JSON, os dados precisam
      ser exatamente os mesmos que serao carregados do PDF""",
      backstory="Voce e um leitor de dados, e sempre teve a responsabilidade de ler dados de um arquivo e passar para o formato JSON",
      verbose=True,
      llm=llm,
  )

  carregar_curriculo = Task(
  description = f"""
  Os dados devem ser carregados de {texto}

  Aja como um especialista em análise de currículos para extração de dados estruturados no formato JSON. Sua tarefa é processar o texto de um arquivo PDF contendo um currículo, identificar as informações pedidas abaixo, e retornar exclusivamente um objeto JSON conforme o exemplo fornecido, sem incluir quaisquer outros textos adicionais. Importante: Não deve haver duplicação de chaves no JSON.

  Instruções: Campos obrigatórios e estrutura do JSON: O JSON deve conter:

  about: informações gerais da pessoa.

  name: Nome completo do dono do currículo.
  position: Profissão ou cargo atual/pretendido.
  contact:
  phone: Número de telefone (caso existam múltiplos, escolher o primeiro listado).
  email: Endereço de e-mail.
  website: Site pessoal ou portfólio (se disponível).
  address: Endereço completo ou apenas o logradouro, incluindo CEP, se fornecido.
  professional_objective: Texto sobre o objetivo profissional ou um resumo sobre a pessoa, caso seja encontrado.
  experience_skills_education:

  education: Formação acadêmica (nome do curso, instituição, datas de início e término, e anotações, se disponíveis).
  skills: Habilidades em formato de palavras-chave (ex.: "Python", "Marketing", "Comunicação").
  experience: Experiência profissional (nome do cargo, empresa, datas de início e término, e uma descrição, se disponível).
  languages: Idiomas listados no currículo, com o nível de proficiência para cada idioma.
  additional_courses: Cursos adicionais, workshops ou certificações (nome do curso, instituição, datas de início e término, e anotações, se disponíveis).
  Observações importantes:

  Se alguma informação não estiver disponível no currículo, a chave correspondente deve ser mantida no JSON com um valor "" ou uma lista vazia ([]).
  Se datas de início ou término estiverem ausentes, substitua pelo ano atual.
  Não adicione informações que não estejam explicitamente mencionadas no currículo.
  Caso um campo já tenha sido preenchido, não repita a chave. Por exemplo, se o campo about já estiver presente, não inclua novamente em outro ponto do JSON.
  Linguagem: Os currículos podem estar em português ou inglês, extraia as informações independentemente do idioma.
  Saída: Retorne somente o JSON, sem qualquer outro texto ou explicação, com todas as chaves únicas. Não repita as chaves do JSON.    

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
      description="Curriculo de uma pessoa",
      tasks=[carregar_curriculo],
      llm=llm,
      verbose=True,
      agents=[Leitor],
      expected_output="JSON"
  )

  crew_output =crew.kickoff()

  crew_json = json.loads(crew_output.raw)

  return json.dumps(crew_json, indent=2, ensure_ascii=False)

