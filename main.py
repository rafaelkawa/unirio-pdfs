import os
from PyPDF2 import PdfReader
from elasticsearch import Elasticsearch

# Função para extrair texto de um PDF
def extract_text_from_pdf(pdf_path):
    try:
        print(f"Extraindo texto de {pdf_path}...")
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)  # Usa len(reader.pages) para obter o número de páginas
        text = ""
        for page_num in range(num_pages):
            text += reader.pages[page_num].extract_text()
        print(f"Texto extraído com sucesso de {pdf_path}.")
        return text
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {str(e)}")
        return None

# Função para indexar o texto no Elasticsearch
def index_text(es, index_name, text, doc_id):
    try:
        print(f"Indexando documento {doc_id}...")
        res = es.index(index=index_name, id=doc_id, body={"content": text})
        print(f"Documento {doc_id} indexado com sucesso.")
    except Exception as e:
        print(f"Erro ao indexar documento {doc_id}: {str(e)}")

# Função para buscar no Elasticsearch
def search_in_elasticsearch(es, index_name, query, description):
    try:
        print(f"Buscando: {description}")
        res = es.search(index=index_name, body={"query": query})
        
        if 'hits' in res and res["hits"]["total"]["value"] > 0:
            print(f"Resultados encontrados para '{description}':")
            for hit in res["hits"]["hits"]:
                print(f"Documento encontrado: {hit['_id']} | Conteúdo: {hit['_source']['content'][:200]}...\n")
                save_search_result(description, hit['_source']['content'], hit['_id'])
        elif 'aggregations' in res:
            print(f"Resultados de agregação encontrados para '{description}':")
            agg_results = res["aggregations"]["common_words"]["buckets"]
            for bucket in agg_results:
                print(f"Palavra: {bucket['key']}, Contagem: {bucket['doc_count']}")
        else:
            print(f"Nenhum resultado encontrado para '{description}'.")
    except Exception as e:
        print(f"Erro ao buscar '{description}': {str(e)}")

# Função para salvar o resultado da busca em um arquivo de texto
def save_search_result(query, content, doc_id):
    directory = './resultados'  # Define a pasta 'resultados'
    if not os.path.exists(directory):  # Verifica se a pasta já existe
        os.makedirs(directory)  # Cria a pasta se não existir
    
    file_name = f"{directory}/resultado_{doc_id}_{query}.txt"  # Define o caminho completo
    with open(file_name, 'w', encoding='utf-8') as file:
        print(f"Salvando resultado da busca por '{query}' no arquivo {file_name}...")
        file.write(content)
    print(f"Resultado salvo com sucesso em {file_name}.")

# Configuração do Elasticsearch
es = Elasticsearch([{"host": "localhost", "port": 9200}])
index_name = "boletins"

# Verifica se o índice já existe, e se não, cria um
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

# Diretório onde os PDFs estão localizados
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

# Lista de queries mais complexas
queries = [
    {
        "description": "Busca por termo 'Computação'",
        "query": {
            "match": {
                "content": "Computação"
            }
        }
    },
    {
        "description": "Busca por data específica (2023)",
        "query": {
            "range": {
                "publication_date": {
                    "gte": "2023-01-01",
                    "lte": "2023-12-31"
                }
            }
        }
    },
    {
        "description": "Busca por múltiplos termos 'Computação' e 'universidade'",
        "query": {
            "bool": {
                "must": [
                    {"match": {"content": "Computação"}},
                    {"match": {"content": "universidade"}}
                ]
            }
        }
    },
    {
        "description": "Busca usando regex para variações de 'Computação'",
        "query": {
            "regexp": {
                "content": "Comp.*"
            }
        }
    },
    {
        "description": "Agregação para contagem de palavras mais comuns",
        "query": {
            "aggs": {
                "common_words": {
                    "terms": {
                        "field": "content.keyword",
                        "size": 10  # Número de palavras mais comuns a retornar
                    }
                }
            }
        }
    },
    {
        "description": "Busca por similaridade (Fuzzy Search) para 'Computação'",
        "query": {
            "fuzzy": {
                "content": {
                    "value": "Computação",
                    "fuzziness": "AUTO"
                }
            }
        }
    }
]

# Testa todas as buscas e salva os resultados em arquivos
for query_info in queries:
    search_in_elasticsearch(es, index_name, query_info["query"], query_info["description"])

print("Todas as consultas foram realizadas e os resultados foram salvos.")
