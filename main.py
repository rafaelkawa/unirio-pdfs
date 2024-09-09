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

# Buscar no Elasticsearch e salvar resultados em arquivos de texto
def search_in_elasticsearch(es, index_name, query, description):
    try:
        print(f"Buscando: {description}")
        res = es.search(index=index_name, body={"query": query})

        result_text = f"Resultados para '{description}':\n"

        if 'hits' in res and res["hits"]["total"]["value"] > 0:
            doc_ids = set()
            for hit in res["hits"]["hits"]:
                doc_ids.add(hit['_id'])
                result_text += f"Documento encontrado: {hit['_id']} | Conteúdo: {hit['_source']['content'][:200]}...\n"
            result_text += f"\nTermo '{description}' encontrado em {len(doc_ids)} arquivos distintos.\n"
        elif 'aggregations' in res:
            result_text += f"Resultados de agregação encontrados para '{description}':\n"
            agg_results = res["aggregations"]["common_words"]["buckets"]
            for bucket in agg_results:
                result_text += f"Palavra: {bucket['key']}, Contagem: {bucket['doc_count']}\n"
        else:
            result_text += f"Nenhum resultado encontrado para '{description}'.\n"

        save_search_result(description, result_text)
    except Exception as e:
        print(f"Erro ao buscar '{description}': {str(e)}")


def save_search_result(query, result_text):
    directory = './resultados'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_name = f"{directory}/resultado_{query}.txt"
    with open(file_name, 'w', encoding='utf-8') as file:
        print(f"Salvando resultado da busca por '{query}' no arquivo {file_name}...")
        file.write(result_text)
    print(f"Resultado salvo com sucesso em {file_name}.")

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
            doc_id = filename.split(".")[0]  
            index_text(es, index_name, text, doc_id)
        else:
            print(f"Falha ao extrair texto de {pdf_path}")

# Lista de queries a serem alteradas para busca
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
