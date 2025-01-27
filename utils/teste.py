import sqlite3
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
