import os
from PyPDF2 import PdfReader
from elasticsearch import Elasticsearch

# Extrair o texto do pdf
def extract_text_from_pdf(pdf_path):
    try:
        print(f"Extraindo texto de {pdf_path}...")
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        text = ""
        for page_num in range(num_pages):
            text += reader.pages[page_num].extract_text()
        print(f"Texto extraído com sucesso de {pdf_path}.")
        return text
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {str(e)}")
        return None

# Indexar o texto no Elasticsearch
def index_text(es, index_name, text, doc_id):
    try:
        print(f"Indexando documento {doc_id}...")
        res = es.index(index=index_name, id=doc_id, body={"content": text})
        print(f"Documento {doc_id} indexado com sucesso.")
    except Exception as e:
        print(f"Erro ao indexar documento {doc_id}: {str(e)}")

# Configuração do Elasticsearch
es = Elasticsearch([{"host": "localhost", "port": 9200}])
index_name = "boletins"

if not es.indices.exists(index=index_name):
    print(f"Criando índice '{index_name}'...")
    es.indices.create(
        index=index_name,
        body={
            "mappings": {
                "properties": {
                    "content": {"type": "text"}
                }
            }
        }
    )
    print(f"Índice '{index_name}' criado com sucesso.")

pdf_directory = './boletins'

# Processa e indexa cada PDF
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        text = extract_text_from_pdf(pdf_path)
        if text:
            doc_id = filename.split(".")[0]  # Usa o nome do arquivo como ID do documento
            index_text(es, index_name, text, doc_id)
        else:
            print(f"Falha ao extrair texto de {pdf_path}")

print("Indexação completa.")
