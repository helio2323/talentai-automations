from driver import Navegador
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import sqlite3
import json

def is_page_exists(navegador):
    try:
        # Aguarda até 10 segundos para o elemento de erro aparecer
        error_element = WebDriverWait(navegador.driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.artdeco-empty-state__headline')))
        
        # Verifica se o texto "Esta página não existe" está no elemento
        if 'Esta página não existe' in error_element.text:
            # Se necessário, você pode adicionar um return ou outro comportamento
            # para interromper ou redirecionar o fluxo do seu código aqui.
            return False
        else:
            return True

    except TimeoutException:
        # Se o elemento não for encontrado dentro do tempo, segue normalmente
        return True

def is_page_is_not_found(navegador):
    try:
        # Espera até que o elemento com texto 'Página não encontrada' apareça
        navegador.wait.until(EC.presence_of_element_located((By.ID, 'i18n_pt_BR')))
    except TimeoutException:
        # Se o tempo expirar e não encontrar o texto, retorna False
        return False
    return True  # Se encontrar o texto, retorna True

def gerar_query(cargos = [], habilidades = [], bancos_dados = [], ferramentas = [], localizacoes = [], empresa=None):
    # Criar a parte da query para os cargos
    cargos_query = " OR ".join([f'"{cargo}"' for cargo in cargos])
    
    # Criar a parte da query para as habilidades
    habilidades_query = " OR ".join([f'"{habilidade}"' for habilidade in habilidades])
    
    # Criar a parte da query para os bancos de dados
    bancos_dados_query = " OR ".join([f'"{banco}"' for banco in bancos_dados])
    
    # Criar a parte da query para as ferramentas
    ferramentas_query = " OR ".join([f'"{ferramenta}"' for ferramenta in ferramentas])
    
    # Criar a parte da query para as localizações
    localizacoes_query = " OR ".join([f'"{localizacao}"' for localizacao in localizacoes])
    
    # Adicionar a empresa, se fornecida
    empresa_query = f' "{empresa}"' if empresa else ""
    
    # Montar a query final
    query = (f'site:linkedin.com/in/ ({cargos_query}) ({habilidades_query}) '
             f'({bancos_dados_query}) ({ferramentas_query}) ({localizacoes_query}){empresa_query}')
        
    return query

# Exemplo de uso da função
cargos = ["Backend Developer", "Backend Engineer", "Desenvolvedor Backend", "Engenheiro de Software", "Software Engineer"]
habilidades = ["Python", "Django", "Flask", "FastAPI", "REST API", "GraphQL", "Microservices"]
bancos_dados = ["SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB"]
ferramentas = ["Docker", "Kubernetes", "Git", "GitHub", "CI/CD", "DevOps"]
localizacoes = ["Brasil", "Brazil", "Remoto", "Remote"]



"""query = gerar_query(cargos, habilidades, bancos_dados, ferramentas, localizacoes)
google_query = 'https://www.google.com.br/search?q=' + query
print(google_query)"""


def wait_for_captcha(navegador):

    try:
        # Aguarda até o elemento estar presente
        WebDriverWait(navegador.driver, 120).until(EC.presence_of_element_located((By.CLASS_NAME, "HZVG1b.Tg7LZd")))

        print("Elemento encontrado!")
    except TimeoutException:
        print("Elemento não encontrado dentro do tempo especificado.")
        # Fecha o navegador em caso de erro
        navegador.quit()
        # Interrompe a execução do código
        raise SystemExit("Execução encerrada devido a erro.")
    
def get_google_results(navegador, max_candidates):
    # Determina o número de páginas a serem processadas
    max_candidates = round(max_candidates / 5)
    perfis = []  # Lista para armazenar todos os perfis

    for i in range(max_candidates):
        # Busca elementos na página atual
        google_results = navegador.driver.find_elements(By.XPATH, '//span[@jscontroller="msmzHf"]')
        print(f"Processando candidato {i+1} de {max_candidates}")

        for result in google_results:
            try:
                # Tentando obter o link
                try:
                    link = result.find_element(By.TAG_NAME, "a").get_attribute("href")

                    # Normaliza o prefixo para remover qualquer idioma ou região desnecessários
                    for prefix in ["/pt", "/en", "/es", "/fr", "/de"]:  # Adicione outros idiomas, se necessário
                        link = link.replace(prefix, "")

                    # Remove o prefixo "https://br." para uniformizar os links
                    link = link.replace("https://br.", "https://")

                    # Remove qualquer prefixo antes de linkedin.com (cm., ke., etc.)
                    link = link.split('linkedin.com', 1)[-1]  # Mantém a parte após 'linkedin.com'
                    link = "https://linkedin.com" + link  # Adiciona o prefixo padrão 'https://linkedin.com'

                except:
                    link = "Link não encontrado"


                # Adicionando os dados à lista de perfis
                perfis.append({
                    "link": link,
                    "nome": "",
                    "skills": "",
                    "sobre": "",
                    "cargo": "",
                    "experiencia": [],
                    "educacao": [],
                    "certificacoes": [],
                    "contato": {
                        "email": "",
                        "telefone": "",
                        "linkedin": "",
                        "github": ""
                    }
                })
            except Exception as e:
                print(f"Erro ao processar candidato: {e}")
        
        # Avança para a próxima página
        navegador.click("ID", "pnnext")

    return perfis


def get_linkedin_profile(**kwargs):

    cookie = {
    "name": "li_at",
    "value": os.environ["LINKEDIN_COOKIE"],
    "domain": ".linkedin.com"
}

    navegador = Navegador()


    navegador.get('https://www.linkedin.com/')
    navegador.driver.add_cookie(cookie)

    navegador.get('https://www.google.com.br/')

    query = gerar_query(cargos = kwargs.get("cargos", []), 
                habilidades = kwargs.get("habilidades", []), 
                bancos_dados = kwargs.get("bancos_dados", []), 
                ferramentas = kwargs.get("ferramentas", []), 
                localizacoes = kwargs.get("localizacoes", [])
                )
    print(query)    
    navegador.get(f'https://www.google.com.br/search?q={query}')

    wait_for_captcha(navegador)

    max_interactions = kwargs.get("max_interactions", 5)

    google_result = get_google_results(navegador, max_interactions)

    navegador.close()
    

    return google_result

    

def get_certifications(navegador, profile_url):
    # pega certificacoes

    import time
    import json

    certification_url = profile_url + "/details/certifications/"

    navegador.get(certification_url)
    if not is_page_exists(navegador):
        return []
    # tratar caso nao tenha certificacoes
    try:
        navegador.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.t-20.t-bold.ph3.pt3.pb2')))


        navegador.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        html = navegador.driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        certification_sections = soup.select('.pvs-list__paged-list-item')

        certifications_data = []

        # Iterando pelas seções de certificações
        for section in certification_sections:
            try:
                # Extraindo informações específicas
                certification_name = section.select_one('.mr1.hoverable-link-text.t-bold span[aria-hidden="true"]').get_text(strip=True) if section.select_one('.mr1.hoverable-link-text.t-bold span[aria-hidden="true"]') else "N/A"
                issuer = section.select_one('.t-14.t-normal span[aria-hidden="true"]').get_text(strip=True) if section.select_one('.t-14.t-normal span[aria-hidden="true"]') else "N/A"
                issue_date = section.select_one('.pvs-entity__caption-wrapper span[aria-hidden="true"]').get_text(strip=True) if section.select_one('.pvs-entity__caption-wrapper span[aria-hidden="true"]') else "N/A"
                credential_id = section.select_one('.t-14.t-normal.t-black--light span[aria-hidden="true"]').get_text(strip=True) if section.select_one('.t-14.t-normal.t-black--light span[aria-hidden="true"]') else "N/A"
                school_url = section.select_one('a.optional-action-target-wrapper[href]')['href'] if section.select_one('a.optional-action-target-wrapper[href]') else "N/A"
                credential_url = section.select_one('a.artdeco-button[href]')['href'] if section.select_one('a.artdeco-button[href]') else "N/A"
                logo_element = soup.select_one('img[src*="company-logo_100_100"]')
                logo_url = logo_element.get('src') if logo_element else "N/A"
                
                # Adicionando ao JSON
                certifications_data.append({
                    "certification_name": certification_name,
                    "issuer": issuer,
                    "issue_date": issue_date,
                    "credential_id": credential_id,
                    "credential_url": credential_url,
                    "school_url": school_url,
                    "school_logo_url": logo_url
                })
            except Exception as e:
                print(f"Erro ao processar uma seção: {e}")

        # Salvando como JSON
        """with open("certifications.json", "w", encoding="utf-8") as f:
            json.dump(certifications_data, f, ensure_ascii=False, indent=4)"""
        
        return certifications_data

    except TimeoutException:
        return [{
            "certification_name": "N/A",
            "issuer": "N/A",
            "issue_date": "N/A",
            "credential_id": "N/A",
            "credential_url": "N/A",
            "school_url": "N/A"
        }]
    print("Dados de certificações extraídos e salvos em 'certifications.json'.")


def get_education(navegador, profile_url):
    # pega educacao
    import time
    import json

    education_url = profile_url + "/details/education/"
    #class t-20 t-bold ph3 pt3 pb2
    navegador.get(education_url)
    if not is_page_exists(navegador):
        return []
    try:
        navegador.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.t-20.t-bold.ph3.pt3.pb2')))

        navegador.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        html = navegador.driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        education_sections = soup.select('.pvs-list__paged-list-item')

        education_data = []

        for section in education_sections:
            try:
                # Extraindo informações específicas
                institution = section.select_one('.mr1.hoverable-link-text.t-bold span[aria-hidden="true"]').get_text(strip=True) if section.select_one('.mr1.hoverable-link-text.t-bold span[aria-hidden="true"]') else "N/A"
                degree = section.select_one('.t-14.t-normal span[aria-hidden="true"]').get_text(strip=True) if section.select_one('.t-14.t-normal span[aria-hidden="true"]') else "N/A"
                dates = section.select_one('.pvs-entity__caption-wrapper span[aria-hidden="true"]').get_text(strip=True) if section.select_one('.pvs-entity__caption-wrapper span[aria-hidden="true"]') else "N/A"
                logo_element = soup.select_one('img[src*="company-logo_100_100"]')
                logo_url = logo_element.get('src') if logo_element else "N/A"


                # Adicionando ao JSON
                education_data.append({
                    "institution": institution,
                    "degree": degree,
                    "dates": dates,
                    "school_logo_url": logo_url
                })
            except Exception as e:
                print(f"Erro ao processar uma seção: {e}")

        # Salvando como JSON
        """with open("education.json", "w", encoding="utf-8") as f:
            json.dump(education_data, f, ensure_ascii=False, indent=4)"""
            
        return education_data
    except TimeoutException:
        return [{
            "institution": "N/A",
            "degree": "N/A",
            "dates": "N/A"
        }]


def get_experiences(navegador, profile_url):

    import json
    import time
    experience_url = profile_url + "/details/experience/"

    navegador.get(experience_url)
    if not is_page_exists(navegador):
        return []
    
    try:
    #aguarda a pagina carregar
        navegador.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pvs-list__paged-list-item')))
        #scroll para baixo demorando 2 segundos
        navegador.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Extraindo o HTML renderizado
        html = navegador.driver.page_source

        # Parseando com BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Buscando as seções de experiência
        experience_sections = soup.select('.pvs-list__paged-list-item')  # Substitua pelo seletor correto

        experiences = []

        for section in experience_sections:
            try:
                job_title = section.select_one('.mr1.t-bold').get_text(strip=True) if section.select_one('.mr1.t-bold') else "N/A"
                company = section.select_one('.t-14.t-normal').get_text(strip=True) if section.select_one('.t-14.t-normal') else "N/A"
                duration = section.select_one('.pvs-entity__caption-wrapper').get_text(strip=True) if section.select_one('.pvs-entity__caption-wrapper') else "N/A"
                #classe das competencias display-flex align-items-center t-14 t-normal t-black
                description = section.select_one('.display-flex.align-items-center.t-14.t-normal.t-black')  # Substitua com o seletor correto
                description_text = description.get_text(strip=True) if description else "N/A"

                #pega a imagem da empresa
                logo_element = soup.select_one('img[src*="company-logo_100_100"]')
                logo_url = logo_element.get('src') if logo_element else "N/A"

                competencies_section = section.select_one('.display-flex.align-items-center.t-14.t-normal.t-black')
                
                # Adicionando ao JSON
                experiences.append({
                    "job_title": job_title,
                    "company": company,
                    "duration": duration,
                    "description": description_text,
                    "company_logo_url": logo_url
                })
            except Exception as e:
                print(f"Erro ao processar uma seção: {e}")

        # Salvando como JSON
        """with open("experiences.json", "w", encoding="utf-8") as f:
            json.dump(experiences, f, ensure_ascii=False, indent=4)"""
        
        return experiences
    except TimeoutException:
        return [{
            "job_title": "N/A",
            "company": "N/A",
            "duration": "N/A",
            "description": "N/A"
        }]
# Fechando o navegador.driver


def update_linkedin_profile(linkedin_profile, update_profile=True):

    import dotenv
    import sqlite3

    dotenv.load_dotenv()

    cookie = {
        "name": "li_at",
        "value": os.environ["LINKEDIN_VISITOR_ID"],
        "domain": ".linkedin.com"
    }

    navegador = Navegador()

    navegador.get('https://www.linkedin.com/feed/')

    navegador.driver.add_cookie(cookie) 

    linkedin_prof = linkedin_profile

    for profile in linkedin_prof:

        #verifica se o perfil ja existe no banco de dados
        conn = sqlite3.connect("profiles.db")
        cursor = conn.cursor()

        cursor.execute("SELECT link FROM profile WHERE link = ?", (profile['link'],))

        if cursor.fetchone() is not None and update_profile == False:
            continue

        if profile['link'] == "Link não encontrado":
            continue
        print(f"Coletando dados do perfil numero {linkedin_prof.index(profile)} do total de {len(linkedin_prof)}")
        profile_url = profile['link']

        #carregar o perfil
        navegador.get(profile_url)
        
        if not is_page_exists(navegador):
            #pula o perfil
            continue

        if is_page_is_not_found(navegador):
            #pula o perfil
            continue

        soup = BeautifulSoup(navegador.driver.page_source, 'html.parser')
        #scrola a pagina e aguarda a pagina carregar
        navegador.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            # Aumentando o tempo de espera para 20 segundos
            name_element = WebDriverWait(navegador.driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.inline.t-24.v-align-middle.break-words'))
            )
            name = name_element.text.strip() if name_element else "N/A"
        except TimeoutException:
            print("Nome não encontrado. Pode ser uma página de erro.")
            name = "N/A"

        # Verifique se name_element é um objeto BeautifulSoup e use get_text apenas se não for None
        

        try:

            photo_element = soup.select_one('img.pv-top-card-profile-picture__image--show.evi-image')
            photo_url = photo_element.get('src') if photo_element else "N/A"

            headline = soup.find('div', {'class': 'text-body-medium break-words'})
            headline = headline.get_text().strip()

            about = soup.find('div', {'class': 'display-flex ph5 pv3'}) if soup.find('div', {'class': 'display-flex ph5 pv3'}) else "N/A"
        except TimeoutException:
            headline = "N/A"
            about = "N/A"
            photo_url = "N/A"
        if about == "N/A":
            about = "N/A"
        else:
            about = about.get_text().strip()

        #atualiza o perfil
        profile['nome'] = name
        profile['skills'] = headline
        profile['sobre'] = about
        profile['foto'] = photo_url
        #coleta de experiencia
        print('-'*100)
        print(f"coletando experiencia, educacao e certificacoes de {name}")
        experiences = get_experiences(navegador, profile_url)
        profile['experiencia'] = experiences
        #coleta de educacao
        education = get_education(navegador, profile_url)
        profile['educacao'] = education
        #coleta de certificacoes
        certifications = get_certifications(navegador, profile_url)
        profile['certificacoes'] = certifications
        
        print(f"dados de {name} coletados com sucesso")
        print('-'*100)

    navegador.close()
    
    return linkedin_prof



def salvar_ou_atualizar_perfis_em_banco(dados, nome_arquivo_db="profiles.db"):
    
    """
    Salva ou atualiza uma lista de perfis no banco de dados SQLite.

    :param dados: Lista de dicionários representando os perfis.
    :param nome_arquivo_db: Nome do arquivo do banco de dados SQLite.
    """
    # Conexão com o banco de dados
    conn = sqlite3.connect(nome_arquivo_db)
    cursor = conn.cursor()

    # Certificar-se de que a tabela existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profile (
        link TEXT PRIMARY KEY,
        nome TEXT,
        skills TEXT,
        sobre TEXT,
        cargo TEXT,
        experiencia TEXT,
        educacao TEXT,
        certificacoes TEXT,
        contato_email TEXT,
        contato_telefone TEXT,
        contato_linkedin TEXT,
        contato_github TEXT,
        foto TEXT
    );
    ''')

    for perfil in dados:
        link = perfil.get("link", "")
        
        # Verificar se o link já existe na tabela
        cursor.execute("SELECT link FROM profile WHERE link = ?", (link,))
        if cursor.fetchone() is not None:
            # Atualizar o registro existente
            cursor.execute('''
            UPDATE profile
            SET nome = ?, skills = ?, sobre = ?, cargo = ?, experiencia = ?, 
                educacao = ?, certificacoes = ?, contato_email = ?, contato_telefone = ?, 
                contato_linkedin = ?, contato_github = ?, foto = ?
            WHERE link = ?
            ''', (
                perfil.get("nome", ""),
                perfil.get("skills", ""),
                perfil.get("sobre", ""),
                perfil.get("cargo", ""),
                json.dumps(perfil.get("experiencia", [])),  # Serializar lista como JSON
                json.dumps(perfil.get("educacao", [])),  # Serializar lista como JSON
                json.dumps(perfil.get("certificacoes", [])),  # Serializar lista como JSON
                perfil.get("contato", {}).get("email", ""),
                perfil.get("contato", {}).get("telefone", ""),
                perfil.get("contato", {}).get("linkedin", ""),
                perfil.get("contato", {}).get("github", ""),
                perfil.get("foto", ""),
                link
            ))
            print(f"Registro com o link '{link}' atualizado com sucesso.")
        else:
            # Inserir um novo registro
            cursor.execute('''
            INSERT INTO profile (
                link, nome, skills, sobre, cargo, experiencia, educacao, certificacoes,
                contato_email, contato_telefone, contato_linkedin, contato_github, foto
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                link,
                perfil.get("nome", ""),
                perfil.get("skills", ""),
                perfil.get("sobre", ""),
                perfil.get("cargo", ""),
                json.dumps(perfil.get("experiencia", [])),  # Serializar lista como JSON
                json.dumps(perfil.get("educacao", [])),  # Serializar lista como JSON
                json.dumps(perfil.get("certificacoes", [])),  # Serializar lista como JSON
                perfil.get("contato", {}).get("email", ""),
                perfil.get("contato", {}).get("telefone", ""),
                perfil.get("contato", {}).get("linkedin", ""),
                perfil.get("contato", {}).get("github", ""),
                perfil.get("foto", "")
            ))
            print(f"Registro com o link '{link}' salvo com sucesso.")

    # Confirmar transações e fechar conexão
    conn.commit()
    conn.close()
    print(f"Processamento concluído. Banco de dados atualizado: {nome_arquivo_db}!")


def get_google_profiles(cargos, habilidades, ferramentas, localizacoes, max_interactions, job_bubble_id=None):

    linkedin_profile = []
    update_profile = True

    linkedin_profile = get_linkedin_profile(
        cargos=cargos,
        habilidades=habilidades,
        ferramentas=ferramentas,
        localizacoes=localizacoes,
        max_interactions=max_interactions
    )

    total_profiles = update_linkedin_profile(linkedin_profile, update_profile)

    salvar_ou_atualizar_perfis_em_banco(total_profiles)

    return total_profiles


google_profile = get_google_profiles(
    cargos=["Full Stack Developer"],
    habilidades=["Natural Language Processing", "NLP", "Python", "Machine Learning", "AI", "TensorFlow", "PyTorch", "Deep Learning", "Data Analysis"],
    ferramentas=["Git", "Docker", "AWS", "Google Cloud"],
    localizacoes=["Brasil"],
    max_interactions=100,
    job_bubble_id=1
)

#salva o json
with open("linkedin_profile.json", "w", encoding="utf-8") as f:
    json.dump(google_profile, f, ensure_ascii=False, indent=4)
