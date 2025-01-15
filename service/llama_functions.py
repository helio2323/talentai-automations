def llm_parse(file):
    from llama_parse import LlamaParse
    import os
    llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")

    texto = LlamaParse(
    result_type="markdown",
    parsing_instruction="""
    Extraia o texto do PDF e retorne em markdown
    """,
    api_key=llama_api_key,
    merge = True,
    ).load_data(file)

    texto_processado = []

    for item in texto:
        try:
            texto_processado.append(item.text)
        except:
            pass

    return texto_processado

