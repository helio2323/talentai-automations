from flask import Flask, request, jsonify
import os
from crew import convert_pdf_to_json
from bubble_cv import create_new_resume
import json

app = Flask(__name__)

# Diretório para salvar os arquivos enviados
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Bem-vindo à API Flask!"})

@app.route('/upload', methods=['POST'])
def upload_file():
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
                new_cv = create_new_resume(response, candidate_id="1736209489739x319429545895133200")
            except Exception as e:
                print(f"Erro ao criar currículo: {e}")

            return jsonify({"curriculos": response}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Erro ao processar o arquivo'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)