
import json
import requests

url_resume = "https://talentai.com.br/version-test/api/1.1/obj/talent-resumes/"
url_candidate = "https://talentai.com.br/version-test/api/1.1/obj/talent-candidate-info/"
url_addrress = "https://talentai.com.br/version-test/api/1.1/obj/talent-resume-address/"
url_experience = "https://talentai.com.br/version-test/api/1.1/obj/talent-resume-work-experience/"
url_education = "https://talentai.com.br/version-test/api/1.1/obj/talent-resume-education/"
url_certification = "https://talentai.com.br/version-test/api/1.1/obj/talent-resume-certifications/"

def convert_to_date(date_str):
    from datetime import datetime
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    
    return None

    


def create_data_bubble(json_data, url_bb, operation):
  import json
  url = url_bb
  headers = {
      'Authorization': 'Bearer d523a04a372905b9eb07d90000bee51a',
      'Content-Type': 'application/json'
      }

  if operation == 'create':
    response = requests.request("POST", url, data=json_data, headers=headers)
  if operation == 'update':
    response = requests.request("PATCH", url, data=json_data, headers=headers)

  print(response.text)

  return response

import json

def extrair_dados_curriculos(data, candidate_id):
    """
    Extrai os dados do currículo na posição [0] e retorna um JSON com as informações completas.

    :param data: Dicionário contendo os currículos.
    :param candidate_id: ID do candidato a ser incluído no JSON.
    :return: JSON com os dados extraídos.
    """
    # Verificar se "curriculos" existe e contém elementos
    curriculos = data.get("curriculos", [])
    if not isinstance(curriculos, list) or len(curriculos) == 0:
        return json.dumps({"error": "Nenhum currículo disponível."})
    
    # Considerar apenas o currículo na posição [0]
    curriculo = curriculos[0]  # Acessar o primeiro currículo na lista
    about = curriculo.get("about", {})
    contato = about.get("contact", {})

    # Extrair os dados do currículo
    nome = about.get("name", None)
    posicao = about.get("position", None)
    objetivo_profissional = about.get("professional_objective", None)
    contato_email = contato.get("email", None)
    contato_telefone = contato.get("phone", None)
    contato_website = contato.get("website", None)

    # Construir JSON com os dados extraídos
    json_data = json.dumps({
        "cadidate_email": contato_email,
        "cadidate_id" : candidate_id,
        "cadidate_name" : nome,
        "cadidate_phone" : contato_telefone,
        "candidate_role" : posicao,
        "resume_name" :"Default",
        "summary" : objetivo_profissional
    })

    return json_data


def extrair_endereco_curriculo(data):
    """
    Extrai os dados de endereço do currículo na posição [0] e retorna um JSON com os dados do endereço.

    :param data: Dicionário ou lista contendo os currículos.
    :return: JSON com os dados do endereço extraídos.
    """
    # Verificar se "curriculos" existe e contém elementos
    curriculos = data.get("curriculos", []) if isinstance(data, dict) else data
    if not isinstance(curriculos, list) or len(curriculos) == 0:
        return json.dumps({"error": "Nenhum currículo disponível."})
    
    # Considerar apenas o currículo na posição [0]
    curriculo = curriculos[0]  # Acessar o primeiro currículo na lista
    contato = curriculo.get("about", {}).get("contact", {})
    
    # Acessar a lista de endereços
    endereco_lista = contato.get("address", [])
    
    if not endereco_lista:
        return json.dumps({"error": "Nenhum endereço disponível."})
    
    # Extrair o primeiro endereço da lista
    endereco = endereco_lista[0]
    
    # Usar .get() para acessar os campos, garantindo valores padrão como None
    cidade = endereco.get("city", None)
    pais = endereco.get("country", None)
    estado = endereco.get("state", None)
    rua = endereco.get("street", None)
    cep = endereco.get("zip_code", None)
    
    # Verificar se algum campo está ausente e atribuir "N/A" para esses campos
    endereco_dados = {
        "Cidade": cidade if cidade else "N/A",
        "Pais": pais if pais else "N/A",
        "UF": estado if estado else "N/A",
        "Logradouro": rua if rua else "N/A",
        "CEP": cep if cep else "N/A"
    }
    
    # Retornar os dados como um JSON
    return json.dumps(endereco_dados)



import json

def extrair_experiencia_curriculo(data, resume_id):
    """
    Extrai os dados de experiência profissional do currículo na posição [0] e retorna uma lista com os dados extraídos.

    :param data: Dicionário ou lista contendo os currículos.
    :param resume_id: ID do currículo.
    :return: Lista com os dados de experiência extraídos em formato JSON.
    """
    i = 0
    # Verificar se 'data' é uma lista ou dicionário
    curriculos = data.get("curriculos", []) if isinstance(data, dict) else data
    if not isinstance(curriculos, list) or len(curriculos) == 0:
        return json.dumps({"error": "Nenhum currículo disponível."})
    
    # Considerar apenas o currículo na posição [0]
    curriculo = curriculos[0]
    experiencia_lista = curriculo.get("experience", [])

    if not experiencia_lista:
        return json.dumps({"error": "Nenhuma experiência disponível."})
    
    # Extrair as experiências e organizá-las
    work_list = []
    for experiencia in experiencia_lista:
        i += 1
        instituicao = experiencia.get("institution", None)
        titulo = experiencia.get("title", None)
        descricao = experiencia.get("description", None)
        anos = experiencia.get("years", None)
        start_date = experiencia.get("start_date", None)
        end_date = experiencia.get("end_date", None)
        actual_position = experiencia.get("actual_position", "").lower() == "yes"
        city = experiencia.get("city", None)

        # Criar o dicionário com os dados da experiência
        experiencia_dados = {
            "company_name": instituicao,
            "position": titulo,
            "description": descricao,
            "start_date": convert_to_date(start_date),
            "end_date": convert_to_date(end_date),
            "actual_position": actual_position,
            "experience_order": i,
            "city": city,
            "resume_id": resume_id
        }

        # Criar os dados na API e adicionar ao work_list
        experiencia_dados_json = json.dumps(experiencia_dados)
        id_experiencia = create_data_bubble(experiencia_dados_json, url_experience, "create")
        id_experiencia = id_experiencia.json()

        work_list.append(id_experiencia["id"])

    # Atualizar as experiências no currículo
    url_experience_update = url_resume + resume_id
    data_id_experiencia = json.dumps({"work_experience": work_list})
    create_data_bubble(data_id_experiencia, url_experience_update, "update")

    # Retornar a lista de experiências
    return json.dumps(work_list)

import json

def extrair_education(data, resume_id):
    """
    Extrai os dados de educação do currículo e os envia para a API Bubble.

    :param data: JSON string ou dicionário contendo os currículos.
    :param resume_id: ID do currículo para associar as informações.
    :return: Lista de IDs de educação criados.
    """
    i = 0

    # Verificar se 'data' é uma lista ou um dicionário
    curriculos = data.get("curriculos", []) if isinstance(data, dict) else data
    if not isinstance(curriculos, list) or len(curriculos) == 0:
        return json.dumps({"error": "Nenhum currículo disponível."})

    # Considerar apenas o currículo na posição [0]
    curriculo = curriculos[0]
    educacao_lista = curriculo.get("education", [])

    if not educacao_lista:
        return json.dumps({"error": "Nenhum dado de educação disponível."})

    # Extrair os dados de educação e organizar
    education_list = []
    for education in educacao_lista:
        i += 1
        instituicao = education.get("institution", None)
        titulo = education.get("diploma", None)
        descricao = education.get("description", None)
        anos = education.get("years", None)
        start_date = education.get("start_date", None)
        end_date = education.get("end_date", None)
        atual = education.get("current", "").lower() == "yes"

        # Criar os dados de educação para enviar à API
        education_dados = {
            "institution": instituicao,
            "Diploma": titulo,
            "description": descricao,
            "start_date": convert_to_date(start_date),
            "end_date": convert_to_date(end_date),
            "current": atual,
            "experience_order": i,
            "resume_id": resume_id,
            "degree": education.get("degree", "N/A")
        }

        # Enviar dados para a API Bubble
        education_dados_json = json.dumps(education_dados)
        id_education = create_data_bubble(education_dados_json, url_education, "create")
        id_education = id_education.json()

        education_list.append(id_education["id"])

    # Atualizar o currículo com os IDs de educação
    url_education_update = url_resume + resume_id
    data_id_education = json.dumps({"Education": education_list})

    create_data_bubble(data_id_education, url_education_update, "update")

    # Retornar a lista de IDs de educação criados
    return json.dumps(education_list)



import json

def extrair_certifications(data, resume_id):
    """
    Extrai os dados de certificações do currículo e os envia para a API Bubble.

    :param data: JSON string ou dicionário contendo os currículos.
    :param resume_id: ID do currículo para associar as informações.
    :return: Lista de IDs de certificações criados.
    """
    i = 0

    # Verificar se 'data' é uma lista ou um dicionário
    curriculos = data.get("curriculos", []) if isinstance(data, dict) else data
    if not isinstance(curriculos, list) or len(curriculos) == 0:
        return json.dumps({"error": "Nenhum currículo disponível."})

    # Considerar apenas o currículo na posição [0]
    curriculo = curriculos[0]
    certifications_lista = curriculo.get("additional_courses", [])

    if not certifications_lista:
        return json.dumps({"error": "Nenhum dado de certificações disponível."})

    # Extrair os dados de certificações e organizar
    certifications_list = []
    for certification in certifications_lista:
        i += 1
        curso = certification.get("course", None)
        instituicao = certification.get("institution", None)
        notas = certification.get("notes", None)
        start_date = certification.get("start_date", "")
        end_date = certification.get("end_date", "")

        certification_dados = {
            "certification_name": curso,
            "institution": instituicao,
            "description": notas,
            "experience_order": i,
            "resume_id": resume_id,
        }

        # Enviar dados para a API Bubble
        certification_dados_json = json.dumps(certification_dados)
        id_certification = create_data_bubble(certification_dados_json, url_certification, "create")
        id_certification = id_certification.json()

        certifications_list.append(id_certification["id"])

    # Atualizar o currículo com os IDs de certificações
    url_certification_update = url_resume + resume_id
    data_id_certification = json.dumps({"Certificate": certifications_list})

    create_data_bubble(data_id_certification, url_certification_update, "update")

    # Retornar a lista de IDs de certificações criados
    return json.dumps(certifications_list)



def create_new_resume(data, candidate_id):

    json_data = extrair_dados_curriculos(data, candidate_id)

    result = create_data_bubble(json_data, url_resume, "create")
    result = result.json()
    resume_id = result["id"]

    canidate_data = json.dumps({
        "resumes": [resume_id]
    })

    url_update = url_candidate + candidate_id

    create_data_bubble(canidate_data, url_update, "update")


    """ Cria dado no banco enderecos"""
    dados_endereco = extrair_endereco_curriculo(data)

    print(dados_endereco)

    id_enderecos = create_data_bubble(dados_endereco, url_addrress, "create")

    print(id_enderecos)

    id_enderecos = id_enderecos.json()

    url_endereco_update = url_resume + resume_id

    data_endereco = json.dumps({
        "resume_address" : id_enderecos["id"]
    })

    create_data_bubble(data_endereco, url_endereco_update, "update")

    """ Cria dado no banco experiencias"""
    extrair_experiencia_curriculo(data, resume_id)

    """ Cria dado no banco educacao"""
    extrair_education(data, resume_id)
    
    """ Cria dado no banco certificacoes"""
    extrair_certifications(data, resume_id)

    return resume_id


