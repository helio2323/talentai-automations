from flask import Flask, request, jsonify
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crew import convert_pdf_to_json
from bubble_cv import create_new_resume
from utils.google import search_profiles
from utils.aditionals_functions import create_table_queue, insert_job_queue, update_job_status, get_db_connection
from job_avaliation import avaliation_candidate
import json

app = Flask(__name__)

# Diretório para salvar os arquivos enviados
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Bem-vindo à API Flask!"})


@app.route("/avaliate_candidate", methods=['POST'])
def avaliate_candidate():
    try:
        # Pegando os dados do form-data
        candidate_cv_info = request.form.get("candidate_cv_info")
        job_info = request.form.get("job_info")

        result = avaliation_candidate(candidate_cv_info, job_info)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/upload/<candidate_id>', methods=['POST'])
def upload_file(candidate_id):
    # Verifica se a requisição contém um arquivo
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']

    # Verifica se o arquivo tem um nome válido
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    if file:
        # Define o caminho do arquivo salvo
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        # Salva o arquivo no servidor
        file.save(file_path)

        try:
            # Processa o arquivo salvo
            response = convert_pdf_to_json(file_path)  # Supõe-se que o retorno é um dicionário
            # Remove o arquivo salvo
            os.remove(file_path)

            # Se `response` já é um dicionário, não há necessidade de usar `json.loads()`
            if not isinstance(response, dict):
                response = json.loads(response)

            # Cria o currículo
            print("criando curriculo")
            try:
                new_cv = create_new_resume(response, candidate_id)
            except Exception as e:
                print(f"Erro ao criar currículo: {e}")

            return jsonify({"curriculos": response}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Erro ao processar o arquivo'}), 500

@app.route('/searchprofiles', methods=['POST'])
def search_profiles_route():  # Renomeei para evitar conflito de nome com o import
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado JSON enviado"}), 400

        result = search_profiles(
            cargos=data.get("cargos", []),
            habilidades=data.get("habilidades", []),
            ferramentas=data.get("ferramentas", []),
            localizacoes=data.get("localizacoes", []),
            max_interactions=data.get("max_interactions", 10),
            job_bubble_id=data.get("job_bubble_id", '')
        )

        return jsonify({"message": "Pesquisa realizada com sucesso", "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/add_job", methods=["POST"])
def add_job():
    data = request.get_json()
    
    job_id = data.get("job_id")
    max_candidates = data.get("max_candidates", 10)  # Default value of 10
    cargos = data.get("cargos", [])
    habilidades = data.get("habilidades", [])
    ferramentas = data.get("ferramentas", [])
    localizacoes = data.get("localizacoes", [])
    max_interactions = data.get("max_interactions", 5)
    job_bubble_id = data.get("job_bubble_id")
    
    if not job_id:
        return jsonify({"error": "job_id é obrigatório"}), 400
    
    # Insere o job na fila com os novos parâmetros
    conn = get_db_connection()
    cursor = conn.cursor()
    job_inserted_id = insert_job_queue(job_id, 
                                       max_candidates=max_candidates, 
                                       cargos=cargos, 
                                       habilidades=habilidades, 
                                       ferramentas=ferramentas, 
                                       localizacoes=localizacoes, 
                                       max_interactions=max_interactions, 
                                       job_bubble_id=job_bubble_id)
    conn.close()

    return jsonify({"message": "Job adicionado", "job_id": job_id, "inserted_id": job_inserted_id}), 201



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)