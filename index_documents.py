import os
from PyPDF2 import PdfReader
from elasticsearch import Elasticsearch

pdf_directory = './boletins'

# Conectando ao Elasticsearch
print("Conectando ao Elasticsearch...")
es = Elasticsearch([{"host": "localhost", "port": 9200}])
print("Conexão ao Elasticsearch estabelecida.")

# extrair o texto dos PDFs por página
def extract_text_from_pdf(pdf_path):
    try:
        print(f"Extraindo texto de {pdf_path}...")
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        text = ""
        page_texts = {}  
        
        for page_num in range(num_pages):
            page_content = reader.pages[page_num].extract_text()
            if page_content:
                text += page_content
                page_texts[page_num + 1] = page_content  
                
        print(f"Texto extraído com sucesso de {pdf_path}.")
        return text, page_texts
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {str(e)}")
        return None, None

# indexar o texto e pag no Elasticsearch
def index_text(es, index_name, page_texts, doc_id):
    try:
        for page_num, page_content in page_texts.items():
            print(f"Indexando página {page_num} do documento {doc_id}...")
            res = es.index(index=index_name, id=f"{doc_id}_page_{page_num}", body={
                "content": page_content,
                "doc_id": doc_id,
                "page": page_num
            })
            print(f"Página {page_num} do documento {doc_id} indexada com sucesso.")
    except Exception as e:
        print(f"Erro ao indexar documento {doc_id}: {str(e)}")

# criar o índice no Elasticsearch
def create_index(es, index_name):
    if not es.indices.exists(index=index_name):
        print(f"Criando índice '{index_name}'...")
        es.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "doc_id": {"type": "keyword"},
                        "page": {"type": "integer"}
                    }
                }
            }
        )
        print(f"Índice '{index_name}' criado com sucesso.")
    else:
        print(f"Índice '{index_name}' já existe.")

# indexar todos os PDFs no diretório especificado
def index_all_pdfs(es, index_name, pdf_directory):
    print("Iniciando indexação de todos os PDFs...")
    create_index(es, index_name) 
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            print(f"Processando {filename}...")
            text, page_texts = extract_text_from_pdf(pdf_path)
            if text and page_texts:
                doc_id = filename.split(".")[0] 
                index_text(es, index_name, page_texts, doc_id)
            else:
                print(f"Falha ao extrair texto de {pdf_path}")
    print("Indexação completa.")

# Executa o processo de indexação
index_name = "boletins"  # Nome do índice
index_all_pdfs(es, index_name, pdf_directory)

