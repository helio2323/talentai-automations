import nbformat
from nbconvert import PythonExporter

def load_ipynb_functions(notebook_path):
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    exporter = PythonExporter()
    source_code, _ = exporter.from_notebook_node(notebook)

    exec(source_code, globals())  # Executa o código no escopo global

# Exemplo: Carregar funções do notebook "google.ipynb"
load_ipynb_functions("google.ipynb")


def search_profiles(**kwargs):
    # Agora você pode chamar funções definidas no notebook

    if  kwargs.get("job_bubble_id") !=  "":

        resultado = query, navegador = get_linkedin_profile(
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