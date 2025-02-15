#!/usr/bin/env python
# coding: utf-8

# In[2]:


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import Select
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os




class Navegador:
    def __init__(self):
        # Configurar opções do Chrome
        options = Options()
        options.add_argument("--enable-automation")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--kiosk-printing")
        

        #add plugin
        options.add_extension('./solver.crx')
        
        self.servico = Service(ChromeDriverManager().install())
        
        
        # Inicializar o WebDriver do Chrome com as opções configuradas
        #self.driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub", options=options)
        self.driver = webdriver.Chrome(service=self.servico, options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.by = By
        self.locator = {
            "XPATH": By.XPATH,
            "ID": By.ID,
            "CLASS_NAME": By.CLASS_NAME,
            "LINK_TEXT": By.LINK_TEXT,
            "NAME": By.NAME,
            "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
            "TAG_NAME": By.TAG_NAME,
            "CSS_SELECTOR": By.CSS_SELECTOR
        }        

    def get_session_id (self):
        return self.driver.session_id

    def disable_alert(self):
        self.driver.switch_to.alert.dismiss()

    def element_get_text(self, element, tag):
        if element in self.locator:
            try:
                # Aguardar até que o elemento seja visível e, em seguida, retornar seu texto
                element_text = self.wait.until(EC.visibility_of_element_located((self.locator[element], tag)))
                return element_text
            except TimeoutException:
                print("Elemento não encontrado")   
                  
    def get_elements(self, element, tag):
        if element in self.locator:
            try:
                # Aguardar até que o elemento seja visível e, em seguida, retornar seu texto
                elements = self.wait.until(EC.visibility_of_all_elements_located((self.locator[element], tag)))
                return elements
            except TimeoutException:
                print("Elemento não encontrado")

    def get(self, url):
        # await asyncio.sleep(0)
        self.driver.get(url)
    def close(self):
    #  await asyncio.sleep(0)
        self.driver.close()

    def close_session(self, session_id):
        grid_url = "https://grid.consium.com.br/wd/hub"
        session_url = f"{grid_url}/session/{session_id}"
        response = requests.delete(session_url)
        if response.status_code == 200:
            print("Sessão fechada com sucesso!")
        else:
            print("Falha ao fechar a sessão.")

        return response    
    # Funcao para digitar no elemento           
    def sendkeys(self, element, tag, keys):
    #  await asyncio.sleep(0)
        if element in self.locator:
            try:
                self.wait.until(EC.presence_of_element_located((self.locator[element], tag))).send_keys(keys)
            except TimeoutException:
                print("Elemento não encontrado")
                
    # Funcao para clicar no elemento                
    def click(self, element, tag):
    #  await asyncio.sleep(0)
        if element in self.locator:
            try:
                self.wait.until(EC.visibility_of_element_located((self.locator[element], tag))).click()
            except TimeoutException:    
                print("Elemento não encontrado")


    def get_table_element(self, element, tag):
        try:
            # Obter o conteúdo HTML da tag <tbody>
            html_content = self.wait.until(EC.visibility_of_element_located((self.locator[element], tag))).get_attribute('innerHTML')
            # Extrair dados da tabela e transforma em dataframe
            data = self.table_to_dataframe(html_content)
            qtd_linhas = len(data)
            return data, qtd_linhas
        except TimeoutException:
            print("Elemento não encontrado")

    def table_to_dataframe(self, html_content):

        soup = BeautifulSoup(html_content, 'html.parser')

        # Encontra a tabela desejada (selecionando-a pela classe, id ou outras características)
        table = soup.find('table')

        # Verifica se a tabela foi encontrada
        if table:
            # Inicializa uma lista para armazenar os dados da tabela
            table_data = []
            # Itera sobre as linhas da tabela (<tr>)
            for row in table.find_all('tr'):
                # Inicializa uma lista para armazenar os dados de uma linha
                row_data = []
                # Itera sobre as células da linha (<td>)
                for cell in row.find_all(['td']):
                    # Adiciona o texto da célula à lista de dados da linha
                    value = cell.text.strip()
                    # Verifica se o valor não está vazio
                    if value:
                        row_data.append(value)
                    else:
                        row_data.append(None)
                    # Verifica se a célula contém uma tag de âncora (hiperlink)
                    link = cell.find('a')
                    if link:
                        # Se houver uma tag de âncora, adiciona o link (href) à lista de dados da linha
                        row_data.append(link.get('href'))
                    else:
                        row_data.append(None)
                # Adiciona os dados da linha à lista de dados da tabela
                if row_data:
                    table_data.append(row_data)

            # Imprime os dados da tabela
            
            df = pd.DataFrame(table_data)
            df.to_excel('arquivo.xlsx', index=False)

            return df 
        

                   


# In[3]:


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


# In[4]:


import logging
import sqlite3
import traceback
import datetime
from colorama import Fore, Style, init

# Inicializa o colorama para compatibilidade no Windows
init(autoreset=True)

class SQLiteHandler(logging.Handler):
    def __init__(self, db_path="logs.db"):
        super().__init__()
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                message TEXT,
                email TEXT,
                file_name TEXT,
                line_number INTEGER,
                application_name TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def emit(self, record):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            log_time = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO logs (
                    timestamp, 
                    level, 
                    message, 
                    email, 
                    file_name, 
                    line_number, 
                    application_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_time,
                record.levelname,
                record.getMessage(),
                getattr(record, 'email', None),
                record.pathname,
                record.lineno,
                getattr(record, 'application_name', None)
            ))
            conn.commit()
            conn.close()
        except Exception:
            print("Erro ao salvar log no banco de dados:", traceback.format_exc())

# Classe para colorir logs no console
class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA + Style.BRIGHT
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        formatted_message = super().format(record)
        return f"{log_color}{formatted_message}{Style.RESET_ALL}"

# Configuração do logger
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)

# Remove handlers existentes (se houver)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Configuração do formato do log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Adiciona o SQLiteHandler
sqlite_handler = SQLiteHandler()
sqlite_handler.setFormatter(formatter)
logger.addHandler(sqlite_handler)

# Adiciona um handler para exibir logs no console com cores
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)



# In[5]:


import sqlite3
import json

def salvar_ou_atualizar_perfil_em_banco(perfil, nome_arquivo_db="profiles.db"):
    """
    Salva ou atualiza um único perfil no banco de dados SQLite.

    :param perfil: Dicionário representando o perfil a ser salvo ou atualizado.
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
        foto TEXT,
        id_external_candidate TEXT
    );
    ''')

    link = perfil.get("link", "")
    id_external_candidate = perfil.get("id_external_candidate", "")

    # Verificar se o link já existe na tabela
    cursor.execute("SELECT link FROM profile WHERE link = ?", (link,))
    if cursor.fetchone() is not None:
        # Atualizar o registro existente
        cursor.execute('''
        UPDATE profile
        SET nome = ?, skills = ?, sobre = ?, cargo = ?, experiencia = ?, 
            educacao = ?, certificacoes = ?, contato_email = ?, contato_telefone = ?, 
            contato_linkedin = ?, contato_github = ?, foto = ?, id_external_candidate = ?
        WHERE link = ?
        ''', (
            perfil.get("nome", ""),
            perfil.get("skills", ""),
            perfil.get("sobre", ""),
            perfil.get("cargo", ""),
            json.dumps(perfil.get("experiencia", [])),
            json.dumps(perfil.get("educacao", [])),
            json.dumps(perfil.get("certificacoes", [])),
            perfil.get("contato", {}).get("email", ""),
            perfil.get("contato", {}).get("telefone", ""),
            perfil.get("contato", {}).get("linkedin", ""),
            perfil.get("contato", {}).get("github", ""),
            perfil.get("foto", ""),
            id_external_candidate,
            link
        ))
        print(f"Registro com o link '{link}' atualizado com sucesso.")
    else:
        # Inserir um novo registro
        cursor.execute('''
        INSERT INTO profile (
            link, nome, skills, sobre, cargo, experiencia, educacao, certificacoes,
            contato_email, contato_telefone, contato_linkedin, contato_github, foto, id_external_candidate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            link,
            perfil.get("nome", ""),
            perfil.get("skills", ""),
            perfil.get("sobre", ""),
            perfil.get("cargo", ""),
            json.dumps(perfil.get("experiencia", [])),
            json.dumps(perfil.get("educacao", [])),
            json.dumps(perfil.get("certificacoes", [])),
            perfil.get("contato", {}).get("email", ""),
            perfil.get("contato", {}).get("telefone", ""),
            perfil.get("contato", {}).get("linkedin", ""),
            perfil.get("contato", {}).get("github", ""),
            perfil.get("foto", ""),
            id_external_candidate
        ))
        print(f"Registro com o link '{link}' salvo com sucesso.")

    # Confirmar transações e fechar conexão
    conn.commit()
    conn.close()
    print(f"Processamento concluído. Banco de dados atualizado: {nome_arquivo_db}!")


# In[6]:


def wait_close_popup(navegador):

    navegador.click("XPATH", "/html/body/div[2]/div/div/section/button")



# In[7]:


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



# In[8]:


def is_page_is_not_found(navegador):
    try:
        # Espera até que o elemento com texto 'Página não encontrada' apareça
        navegador.wait.until(EC.presence_of_element_located((By.ID, 'i18n_pt_BR')))
    except TimeoutException:
        # Se o tempo expirar e não encontrar o texto, retorna False
        return False
    return True  # Se encontrar o texto, retorna True


# In[9]:


def gerar_query(cargos = [], habilidades = [], bancos_dados = [], ferramentas = [], localizacoes = [], empresa=None):

    logger.info("Gerando query...")

    try:
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
        logger.info("Query gerada com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao gerar query: {e}")
        raise
        
    return query


# In[10]:


def wait_for_captcha(navegador):

    try:
        # Aguarda até o elemento estar presente
        WebDriverWait(navegador.driver, 240).until(EC.presence_of_element_located((By.CLASS_NAME, "HZVG1b.Tg7LZd")))

        print("Elemento encontrado!")
    except TimeoutException:
        print("Elemento não encontrado dentro do tempo especificado.")
        # Fecha o navegador em caso de erro
        navegador.driver.close()
        # Interrompe a execução do código
        raise SystemExit("Execução encerrada devido a erro.")


# In[11]:


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

                    link.click()

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


# In[12]:


def get_linkedin_profile(**kwargs):

    
    logger.info("Getting linkedin profile")

    try:
        cookie = {
        "name": "li_at",
        "value": os.environ["LINKEDIN_COOKIE"],
        "domain": ".linkedin.com"}

        navegador = Navegador()

        #navegador.get('https://www.linkedin.com/')
        #navegador.driver.add_cookie(cookie)

        #navegador.get('https://www.google.com.br/')

        query = gerar_query(cargos = kwargs.get("cargos", []), 
                    habilidades = kwargs.get("habilidades", []), 
                    bancos_dados = kwargs.get("bancos_dados", []), 
                    ferramentas = kwargs.get("ferramentas", []), 
                    localizacoes = kwargs.get("localizacoes", []))
        print(query)
        navegador.get('https://www.google.com')
        navegador.driver.find_element(By.CLASS_NAME, "gLFyf").send_keys(query)   
        navegador.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[3]/center/input[1]").click()
        #navegador.get(f'https://www.google.com.br/search?q={query}')

        logger.info("Waiting for captcha")
        wait_for_captcha(navegador)
    except Exception as e:
        result = False
        logger.error(e)
        raise e
        return query, navegador, result
    result = True
    return query, navegador, result

    

# In[ ]:


"""import sqlite3
import json

# Conexão com o banco de dados (ou criação do arquivo se não existir)
conn = sqlite3.connect("profiles.db")
cursor = conn.cursor()

# Criação da tabela
cursor.execute('''
CREATE TABLE IF NOT EXISTS profile (
    link TEXT,
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

print("Tabela criada com sucesso!")

# Dados do JSON fornecido
data = {
    "link": "https://linkedin.com/in/joaopedroliveira/en",
    "nome": "Joao Pedro Oliveira",
    "skills": "Data Engineer | CI/CD | Python | Docker | Terraform | AWS Certified",
    "sobre": "Data Engineer with extensive experience in consulting and product companies, specializing in developing and managing complex data infrastructures, ETLs, and public cloud implementations (AWS).Technical Skills: - Proficient in Python, R, SQL, DBT, and tools like Docker and Terraform. - Expertise in developing ETL pipelines for both streaming and batch data. - Extensive experience in building interactive dashboards for stakeholder presentations using tools like Metabase. - Contributor to open-source software as a developer with the Elixir programming language.Experienced with Linux systems and certified as an AWS Cloud Practitioner with two years of experience managing data infrastructure in a regulated financial company. Certification:  AWS Cloud Practitioner (09/2021).Open Source Contributions: Contributor to the Explorer library (gh: elixir-nx/explorer), which adds DataFrames functionality to Elixir.Language Proficiency: Native/Fluent Portuguese Advanced English Basic FrenchAcademic Background: Graduate Research Assistant in the Political Science Department at Emory University (USA). Research Assistant at the Getúlio Vargas Foundation (FGV/EPGE). Data Intern in the Economics Department at PUC-Rio. Research Assistant at the Institute for Applied Economic Research (IPEA). Bachelor's degree in International Relations from PUC-Rio.",
    "cargo": "",
    "experiencia": [],
    "educacao": [],
    "certificacoes": [],
    "contato": {
        "email": "",
        "telefone": "",
        "linkedin": "",
        "github": ""
    },
    "foto": "https://media.licdn.com/dms/image/v2/C4E03AQH3t65XHMHQ4g/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1642634082175?e=1743033600&v=beta&t=Om6aH4hQNx5b57xzDdEoTJbfQsesuMtUmunfYARS3xE"
}

# Inserção de dados
cursor.execute('''
INSERT INTO profile (
    link, nome, skills, sobre, cargo, experiencia, educacao, certificacoes,
    contato_email, contato_telefone, contato_linkedin, contato_github, foto
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    data["link"],
    data["nome"],
    data["skills"],
    data["sobre"],
    data["cargo"],
    json.dumps(data["experiencia"]),  # Serializando lista como JSON
    json.dumps(data["educacao"]),  # Serializando lista como JSON
    json.dumps(data["certificacoes"]),  # Serializando lista como JSON
    data["contato"]["email"],
    data["contato"]["telefone"],
    data["contato"]["linkedin"],
    data["contato"]["github"],
    data["foto"]
))

# Confirmação e encerramento
conn.commit()
print("Dados inseridos com sucesso!")
conn.close()
"""


# In[14]:


import sqlite3
import json

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


# - Colocar no update profile para que salve o usuario no BUBBLE sempre que atualizar o dado
# - Lembrar que deve ser passado o job_bubble_id para que salve o usuario no BUBBLE
# - Avaliar como esse dado vai entrar no BUBBLE se vai utilizar o BD existente ou criar uma nova estrutura de tabelas para receber os dados
# 

# In[15]:


def get_initial_infos_from_profile(navegador):
        # Rola a página e aguarda o carregamento
    navegador.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    try:
        logger.debug("Esperando o elemento 'name' ser carregado...")
        link_profile = navegador.driver.current_url

        # Aumentando o tempo de espera para 20 segundos
        name_element = WebDriverWait(navegador.driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#main-content > section.core-rail.mx-auto.papabear\\:w-core-rail-width.mamabear\\:max-w-\\[790px\\].babybear\\:max-w-\\[790px\\] > div > section > section.top-card-layout.container-lined.overflow-hidden.babybear\\:rounded-\\[0px\\] > div > div.top-card-layout__entity-info-container.flex.flex-wrap.papabear\\:flex-nowrap > div:nth-child(1) > button > h1'))
        )
        name = name_element.text.strip() if name_element else "N/A"
    except TimeoutException:
        logger.error("O elemento 'name' não foi carregado dentro do tempo limite.")
        name = "N/A"

    # Parseia o conteúdo da página com BeautifulSoup
    soup = BeautifulSoup(navegador.driver.page_source, 'html.parser')


    try:
        logger.debug("Esperando o elemento 'photo' ser carregado...")
        photo_element = soup.find('img', {
        'class': 'inline-block relative rounded-[50%] w-16 h-16 top-card-layout__entity-image top-card__profile-image top-card__profile-image--real-image top-card__entity-inner-ring onload shadow-color-shadow shadow-[0_4px_12px] border-2 border-solid border-color-surface mt-[-70px] mb-[14px] papabear:border-4 papabear:mt-[-100px] papabear:mb-[18px] lazy-loaded'
    })
        photo_url = photo_element.get('src') if photo_element else "N/A"

        logger.debug("Esperando o elemento 'headline' ser carregado...")
        headline_element = soup.find('h2', {'class': 'top-card-layout__headline'})
        headline = headline_element.get_text().strip() if headline_element else "N/A"

        logger.debug("Esperando o elemento 'about' ser carregado...")
        about_element = soup.find('div', {'class': 'core-section-container__content'})
        about = about_element.get_text().strip() if about_element else "N/A"

        location = soup.select_one('div.not-first-middot > span').get_text(strip=True)


    except Exception as e:
        logger.error(f"Erro ao extrair informações da página: {e}")
        headline = "N/A"
        about = "N/A"
        photo_url = "N/A",
        location = "N/A"

        return name, headline, about, photo_url, link_profile, location

    logger.info(f"Informacoes iniciais do perfil: {name}, {headline}, {about}, {photo_url}")
    return name, headline, about, photo_url, link_profile, location


# In[16]:


def enter_in_profile(navegador, candidate_range):
    try:
        
        profile_result = navegador.driver.find_elements(By.XPATH, '//span[@jscontroller="msmzHf"]')

        link_elemento = profile_result[candidate_range].find_element(By.XPATH, './/a')
        link_elemento.click()

        return navegador
    except:
        logger.error(f'Erro ao clicar no link do perfil do candidato')
        return navegador


# In[17]:


def get_experiences(navegador):
    import time
    """Coleta experiências profissionais de um perfil no LinkedIn."""
    
    logger.info("Iniciando extração de experiências...")

    try:
        if not is_page_exists(navegador):
            logger.warning("Página de experiências não encontrada.")
            return []

        # Aguarda a página carregar completamente
        logger.info("Aguardando carregamento da página...")
        WebDriverWait(navegador.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'experience-item'))
        )

        # Scroll até o final para carregar todas as experiências
        logger.info("Iniciando scroll infinito...")
        last_height = navegador.driver.execute_script("return document.body.scrollHeight")
        while True:
            navegador.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = navegador.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        logger.info("Scroll finalizado.")

        # Extraindo o HTML atualizado
        html = navegador.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Buscando as seções de experiência
        experience_sections = soup.find_all("li", class_="experience-item")
        logger.info(f"Encontradas {len(experience_sections)} experiências.")

        experiences = []

        for section in experience_sections:
            try:
                job_title = section.select_one('.experience-item__title')
                company = section.select_one('.experience-item__subtitle')
                duration = section.select_one('.date-range')
                location = section.find_all("p", class_="experience-item__meta-item")[-1]

                # Extrai a imagem da empresa corretamente
                logo_element = section.select_one('a.profile-section-card__image-link img')
                logo_url = logo_element.get('src', "N/A") if logo_element else "N/A"





                experience = {
                    "job_title": job_title.get_text(strip=True) if job_title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "duration": duration.get_text(strip=True) if duration else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "company_logo_url": logo_url
                }

                experiences.append(experience)
                logger.info(f"Extraída experiência: {experience['job_title']} - {experience['company']}")

            except Exception as e:
                logger.error(f"Erro ao processar uma seção: {e}", exc_info=True)

        logger.info("Extração concluída com sucesso.")
        return experiences

    except TimeoutException:
        logger.error("Tempo limite excedido ao carregar a página.", exc_info=True)
        return [{
            "job_title": "N/A",
            "company": "N/A",
            "duration": "N/A",
            "location": "N/A",
            "company_logo_url": "N/A"
        }]
    
    except Exception as e:
        logger.error("Erro ao extrair experiências: ", exc_info=True)
        return [{
            "job_title": "N/A",
            "company": "N/A",
            "duration": "N/A",
            "location": "N/A",
            "company_logo_url": "N/A"
        }]


# In[18]:


def get_education(navegador):
    import time
    """Coleta informações educacionais de um perfil no LinkedIn."""

    logger.info("Iniciando extração de informações educacionais...")

    if not is_page_exists(navegador):
        logger.warning("Página de educação não encontrada.")
        return []

    try:
        logger.info("Aguardando carregamento da página de educação...")
        navegador.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.education__list')))

        # Scroll para carregar todas as seções
        navegador.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        html = navegador.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        education_sections = soup.select('.education__list-item')
        logger.info(f"Encontradas {len(education_sections)} instituições de ensino.")

        education_data = []

        for section in education_sections:
            try:
                # Nome da Instituição
                institution_elem = section.select_one('h3 a')
                institution = institution_elem.get_text(strip=True) if institution_elem else "N/A"

                # Grau e Curso
                degree_elements = section.select('h4 span')
                degree = degree_elements[0].get_text(strip=True) if len(degree_elements) > 0 else "N/A"
                course = degree_elements[1].get_text(strip=True) if len(degree_elements) > 1 else "N/A"

                # Datas de estudo
                dates_elem = section.select_one('.date-range time')
                dates = " - ".join([time_elem.get_text(strip=True) for time_elem in section.select('.date-range time')]) if dates_elem else "N/A"

                # URL do logotipo
                logo_elem = section.select_one('img.profile-section-card__image')
                logo_url = logo_elem['src'] if logo_elem and 'src' in logo_elem.attrs else "N/A"

                education_entry = {
                    "institution": institution,
                    "degree": degree,
                    "course": course,
                    "dates": dates,
                    "school_logo_url": logo_url
                }

                education_data.append(education_entry)
                logger.info(f"Extraída educação: {institution} - {degree} ({course})")

            except Exception as e:
                logger.error(f"Erro ao processar uma seção de educação: {e}", exc_info=True)

        logger.info("Extração de educação concluída com sucesso.")
        return education_data

    except TimeoutException:
        logger.error("Tempo limite excedido ao carregar a página de educação.", exc_info=True)
        return [{
            "institution": "N/A",
            "degree": "N/A",
            "course": "N/A",
            "dates": "N/A",
            "school_logo_url": "N/A"
        }]
    except Exception as e:
        logger.error("Erro ao extrair informações educacionais.", exc_info=True)
        return [{
            "institution": "N/A",
            "degree": "N/A",
            "course": "N/A",
            "dates": "N/A",
            "school_logo_url": "N/A"
        }]


# In[19]:


def get_certifications(navegador):
    import time
    from bs4 import BeautifulSoup
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    
    if not is_page_exists(navegador):
        return []
    
    try:
        navegador.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section[data-section="certifications"]'))
        )
        navegador.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        html = navegador.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        certification_sections = soup.select('li.profile-section-card')
        
        certifications_data = []

        for section in certification_sections:
            try:
                certification_name = section.select_one('h3 a')
                certification_name = certification_name.get_text(strip=True) if certification_name else None
                
                if not certification_name or certification_name == "N/A":
                    continue  # Ignorar entradas sem nome de certificação válido
                
                issuer = section.select_one('h4 a')
                issuer = issuer.get_text(strip=True) if issuer else "N/A"
                
                issue_date = section.select_one('div.not-first-middot time')
                issue_date = issue_date.get_text(strip=True) if issue_date else "N/A"
                
                credential_url = section.select_one('a[data-tracking-control-name="public_profile_see-credential"]')
                credential_url = credential_url.get('href') if credential_url else "N/A"
                
                school_url = section.select_one('a.profile-section-card__image-link')
                school_url = school_url.get('href') if school_url else "N/A"
                
                logo_url = section.select_one('img.profile-section-card__image')
                logo_url = logo_url.get('src') if logo_url else "N/A"
                
                certifications_data.append({
                    "certification_name": certification_name,
                    "issuer": issuer,
                    "issue_date": issue_date,
                    "credential_url": credential_url,
                    "school_url": school_url,
                    "school_logo_url": logo_url
                })
            except Exception as e:
                print(f"Erro ao processar uma seção: {e}")
        
        return certifications_data
    
    except TimeoutException:
        return []
    except Exception as e:
        logger.error(f"Erro ao obter certificações: {e}")
        return []


# In[20]:


def extructure_json(initial_infos_candidate, experiences, education, certifications, id_external_candidate):

    json_formated = []
    json_formated.append({
                        "link": initial_infos_candidate[4],
                        "nome": initial_infos_candidate[0],
                        "skills": initial_infos_candidate[1],
                        "sobre": initial_infos_candidate[2],
                        "cargo": "",
                        "experiencia": experiences,
                        "educacao": education,
                        "certificacoes": certifications,
                        "contato": {
                            "email": "",
                            "telefone": "",
                            "linkedin": "",
                            "github": ""
                        },
                        "foto": initial_infos_candidate[3],
                        "id_external_candidate": id_external_candidate
                    })
    
    json_formated = json.dumps(json_formated, indent=4)
    json_formated = json.loads(json_formated)
    
    return json_formated


# In[21]:


def create_address_bubble(initial_infos_candidate):

    import os
    from dotenv import load_dotenv

    load_dotenv()

    url_address = os.getenv("URL_ADDRESS")

    logger.debug("Estruturando os dados para o bubble")
    endereco_dados = {
        "Cidade": initial_infos_candidate[0],
    }

    print(url_address)

    logger.debug("Enviando dados json para o bubble")
    endereco_dados = json.dumps(endereco_dados)
    id_address = create_data_bubble(endereco_dados, url_address, "create")

    id_address = id_address.json()['id']

    return id_address


# In[ ]:


def create_experience_data_bubble(experiences):

    import os
    from dotenv import load_dotenv

    load_dotenv()

    url_experience = os.getenv("URL_EXPERIENCE")
    experiences_list = []

    logger.debug("Criando estrutura JSON e salvando no bubble")
    for experience in experiences:

        experiencia_dados = {
            "company_name": experience["company"],
            "position": experience["job_title"],
            "city": experience["location"],
            "company_logo_url" : experience["company_logo_url"],

        }

        experiencia_dados = json.dumps(experiencia_dados)
        id_experience = create_data_bubble(experiencia_dados, url_experience, "create")
        id_experience = id_experience.json()

        experiences_list.append(id_experience["id"])

    return experiences_list


# In[23]:


def create_education_data_bubble(education):

    import os
    from dotenv import load_dotenv

    load_dotenv()

    url_education = os.getenv("URL_EDUCATION")
    education_list = []


    logger.debug("Criando estrutura JSON e salvando no bubble")

    for edu in education:

        education_dados = {
                "institution": edu["institution"],
                "Diploma": edu["degree"],
                "school_logo_url" : edu["school_logo_url"]
            }
        
        education_dados = json.dumps(education_dados)
        id_education = create_data_bubble(education_dados, url_education, "create")
        id_education = id_education.json()

        education_list.append(id_education["id"])

    return education_list


# In[24]:


def create_certification_data_bubble(certifications):

    import os
    from dotenv import load_dotenv

    load_dotenv()

    url_certification = os.getenv("URL_CERTIFICATION")
    experience_list = []

    logger.debug("Criando estrutura JSON e salvando no bubble")

    for certification in certifications:

        certification_dados = {
            "certification_name": certification["certification_name"],
            "institution": certification["issuer"],
            "school_logo_url": certification["school_logo_url"],
        }

        certification_dados = json.dumps(certification_dados)
        id_certification = create_data_bubble(certification_dados, url_certification, "create")
        id_certification = id_certification.json()

        experience_list.append(id_certification["id"])

    return experience_list


# In[25]:


def create_resume_data_bubble(certification_id, education_id, experience_id, address_id):

    import os
    from dotenv import load_dotenv

    load_dotenv()

    url_resume  = os.getenv('URL_RESUME')

    resume_data = {
        "Certificate": certification_id,
        "Education" : education_id,
        "work_experience" : experience_id,
        "resume_address" : address_id,
        "external_resume" : "yes"
    }

    print(resume_data)

    resume_data = json.dumps(resume_data)
    id_resume = create_data_bubble(resume_data, url_resume, "create")
    id_resume = id_resume.json()

    return id_resume




# In[26]:


def create_external_candidate(initial_infos_candidate, id_resume):

    import os
    from dotenv import load_dotenv

    load_dotenv()
    
    logger.debug("Extruturando o json do candidato")
    url_external = os.getenv('URL_EXTERNAL')

    json_candidate = {
        "external_font" : "Linkedin",
        "first_name" : initial_infos_candidate[0],
        "phone" : "",
        "photo" : initial_infos_candidate[3],
        "resume" : "",
        "skills" : initial_infos_candidate[1],
        "about" : initial_infos_candidate[2],
        "link_linkedin" : initial_infos_candidate[4],
        "resume": id_resume["id"]
    }

    logger.debug("Enviando o json para o bubble")
    json_candidate = json.dumps(json_candidate)
    id_candidate = create_data_bubble(json_candidate, url_external, "create")

    id_candidate = id_candidate.json()

    id_candidate = id_candidate["id"]

    return id_candidate



# In[27]:


def verifica_candidato(navegador, candidate_range):
    logger.info("Verificando se o candidato ja esta cadastrado")

    nome_arquivo_db = 'profiles.db'

    conn = sqlite3.connect(nome_arquivo_db)
    cursor = conn.cursor()

    profile_result = navegador.driver.find_elements(By.XPATH, '//span[@jscontroller="msmzHf"]')

    if not profile_result:
        logger.warning("Nenhum candidato encontrado na página.")
        cursor.close()
        conn.close()
        return False, None

    link_elemento = profile_result[candidate_range].find_element(By.XPATH, './/a')
    link = link_elemento.get_attribute('href')

    cursor.execute('SELECT * FROM profile WHERE link = ?', (link,))
    candidate = cursor.fetchone()  # Retorna uma tupla se houver resultado ou None se não houver

    if candidate is None:
        logger.info("Candidato nao cadastrado, iniciando o cadastro")
        cursor.close()
        conn.close()
        return False, None  # Retorna False e None para indicar que o candidato não foi encontrado
    else:
        logger.info("Candidato ja cadastrado, verificando outro candidato")
        cursor.close()
        conn.close()
        return True, candidate  # Retorna True e os dados do candidato encontrado


# In[28]:


#CONSIDERAR ESSA COMO A FUNCAO QUE ATRELA OS CANDIDATOS AO JOB
def vincula_candidato_job(job_id, id_external_candidate):

    url = "https://consium.com.br/version-test/api/1.1/wf/add_external_candidate"

    parameters = {
        "external_id": [id_external_candidate],
        "job_id": job_id,
    }

    headers = {
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=parameters, headers=headers)

    if resp.status_code == 200:
        print(resp.json())
    else:
        print(f"Erro {resp.status_code}: {resp.text}")


# In[ ]:


def get_candidates_from_google_linkedin(navegador, job_id, max_candidates):


    import os
    import math

    try:

        total_candidates = max_candidates + 5
        perfis = []


        logger.debug(f'Iniciando a busca de um total de candidatos: {total_candidates}')

        #redefine o range para 1 candidate para teste

        #total_candidates = 3
        total_interactions = int(math.ceil(total_candidates / 10))
        print(total_interactions)

        for interactions in range(total_interactions):
            candidate_range = 0
            logger.info(f'Iniciando a busca de um total de candidatos: {total_candidates}')
            logger.info(f'Iniciando a busca do candidato {candidate_range}') #  --- Log
            max_range = 10
            for i in range(max_range):
                print(f"{i} - {candidate_range}")
                try:
                    #antes de prosseguir deve verificar se o usuario ja consta no banco de dados, caso sim deve ser usado o profile existente
                    result, candidate_infos = verifica_candidato(navegador, candidate_range)

                    if result == True:
                        logger.info(f'O candidato {candidate_range} ja consta no banco de dados')
                        vincula_candidato_job(job_id, candidate_infos[13])
                        candidate_range += 1
                        continue

                    logger.info(f'Iniciando a busca do candidato {candidate_range}') #  --- Log
                    enter_in_profile(navegador=navegador, candidate_range=candidate_range)

                    logger.info('Fechando a popup') # --- Log
                    wait_close_popup(navegador=navegador)

                    logger.info('Iniciando o preenchimento dos dados do candidato')  #  --- Log
                    initial_infos_candidate = get_initial_infos_from_profile(navegador=navegador)

                    logger.info('Iniciando a coleta de experiencias')   #  --- Log
                    experiences = get_experiences(navegador)

                    logger.info('Iniciando a coleta de educacao')  #  --- Log
                    education = get_education(navegador)

                    logger.info('Iniciando a coleta de certificacoes')  #  --- Log
                    certifications = get_certifications(navegador)

                    #salva dados no Bubble
                    import traceback

                    try:
                        logger.info('Iniciando a coleta de dados no banco de dados no Bubble')
                        certification_id = create_certification_data_bubble(certifications)
                        education_id = create_education_data_bubble(education)
                        experience_id = create_experience_data_bubble(experiences)
                        address_id = create_address_bubble(initial_infos_candidate)
                        id_resume = create_resume_data_bubble(certification_id, education_id, experience_id, address_id)
                        id_external_candidate = create_external_candidate(initial_infos_candidate, id_resume)
                    except Exception as e:
                        logger.error('Não foi possível salvar os dados no banco de dados')
                        logger.error(f'Erro: {str(e)}')
                        logger.error(traceback.format_exc())  # Captura e exibe o traceback completo
                        navegador.driver.back()
                        continue

                    #--------------------------------------------------------------------------------------------

                    json_data = extructure_json(initial_infos_candidate, experiences, education, certifications, id_external_candidate)
                    #salva dados no banco de dados Sqlite
                    salvar_ou_atualizar_perfil_em_banco(json_data[0])

                    #atrelar o id_external_candidate ao JOB
                    vincula_candidato_job(job_id, id_external_candidate)

                    #retorna para a pagina inicial
                    navegador.driver.back()
                    candidate_range += 1

                except:
                    navegador.driver.back()
                    logger.error('Nao foi possivel processar os dados do candidato')
                    #salva o erro no banco de dados
                    logger.error(f"Erro {traceback.format_exc()}")
                    candidate_range += 1
                    continue

            navegador.click("ID", "pnnext")      

        navegador.driver.quit()
        return {
            "status": "success",
            "message": "Candidatos processados com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro {traceback.format_exc()}")
        navegador.driver.close()
        return {
            "status": "error",
            "message": str(e)
        }


# In[30]:


"""query, navegador = get_linkedin_profile(
    cargos=["Full Stack Developer"],
    habilidades=["Natural Language Processing", "NLP", "Python", "Machine Learning", "AI", "TensorFlow", "PyTorch", "Deep Learning", "Data Analysis"],
    ferramentas=["Git", "Docker", "AWS", "Google Cloud"],
    localizacoes=["Brasil"],
    max_interactions=100,
    job_bubble_id=1
)"""


# In[31]:


#get_candidates_from_google_linkedin(navegador, "1738117388263x970142495908560900", 100)


# #Criar End Point API
# #Criar uma funcao principal que criar os dados no bubble e caso consiga retorna true e ai pode seguir com o cadastro no SQLITE

# In[ ]:


import sqlite3

def limpar_banco_de_dados(nome_arquivo_db="logs.db"):
    """
    Remove todos os registros de todas as tabelas no banco de dados SQLite.

    :param nome_arquivo_db: Nome do arquivo do banco de dados SQLite.
    """
    # Conexão com o banco de dados
    conn = sqlite3.connect(nome_arquivo_db)
    cursor = conn.cursor()

    # Obter todas as tabelas do banco de dados
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()

    if not tabelas:
        print("Nenhuma tabela encontrada no banco de dados.")
    else:
        for tabela in tabelas:
            nome_tabela = tabela[0]
            # Limpar a tabela
            cursor.execute(f"DELETE FROM {nome_tabela};")
            print(f"Tabela '{nome_tabela}' limpa com sucesso.")

        # Confirmar alterações
        conn.commit()

    # Fechar a conexão
    conn.close()
    print(f"Banco de dados '{nome_arquivo_db}' foi completamente limpo.")

#limpar_banco_de_dados()

def search_profiles(**kwargs):
    # Agora você pode chamar funções definidas no notebook

    if  kwargs.get("job_bubble_id") !=  "":

        query, navegador, result = get_linkedin_profile(
            cargos=kwargs.get("cargos", []),
            habilidades=kwargs.get("habilidades", []),
            ferramentas=kwargs.get("ferramentas", []),
            localizacoes=kwargs.get("localizacoes", []),
            max_interactions=kwargs.get("max_interactions", 10),
            job_bubble_id=kwargs.get("job_bubble_id", 1)
        )

        get_candidates_from_google_linkedin(navegador, kwargs.get("job_bubble_id"), kwargs.get("max_interactions", 10))
        return {"status": "Busca realizada com sucesso"}
    else:
        return {"status": "Nao foi possivel buscar perfis"}