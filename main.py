import os
from elasticsearch import Elasticsearch

# buscar no Elasticsearch e contar todas as ocorrências
def search_in_elasticsearch(es, index_name, query, description):
    try:
        print(f"Buscando: {description}")
        

        res = es.search(index=index_name, body={
            "query": query,
            "highlight": {
                "fields": {
                    "content": {}
                }
            }
        }, size=1000) 

        total_hits = res["hits"]["total"]["value"]  
        total_occurrences = 0  
        result_text = f"Resultados para '{description}':\n\n"

        if total_hits > 0:
            doc_ids = set()
            for hit in res["hits"]["hits"]:
                doc_id = hit['_source']['doc_id']
                page_num = hit['_source']['page']
                doc_ids.add(doc_id)

                if "highlight" in hit and "content" in hit["highlight"]:
                    occurrences = hit["highlight"]["content"]
                    num_occurrences = len(occurrences)
                    total_occurrences += num_occurrences  # Soma ao total de ocorrências

                    for occ in occurrences:
                        result_text += f"Documento: {doc_id} | Página: {page_num}\nOcorrência: {occ}\n\n"

            result_text += f"\nTermo '{description}' encontrado em {total_occurrences} ocorrência(s) no total, em {len(doc_ids)} arquivos distintos.\n"
        else:
            result_text += f"Nenhum resultado encontrado para '{description}'.\n"

        save_search_result(description, result_text)
    except Exception as e:
        print(f"Erro ao buscar '{description}': {str(e)}")

# salvar o resultado da busca em um arquivo de texto
def save_search_result(query, result_text):
    directory = './resultados'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_name = f"{directory}/resultado_{query}.txt"
    with open(file_name, 'w', encoding='utf-8') as file:
        print(f"Salvando resultado da busca por '{query}' no arquivo {file_name}...")
        file.write(result_text)
    print(f"Resultado salvo com sucesso em {file_name}.")

# Inicialização do cliente Elasticsearch
es = Elasticsearch([{"host": "localhost", "port": 9200}])
index_name = "boletins"

# Lista de queries a serem alteradas para busca
queries = [
    {
        "description": "Busca",
        "query": {
            "bool": {
                "must": [
                    {"match": {"content": "José Ricardo Cereja"}}  
                ],
                "should": [
                    {"match": {"content": "estágio"}},
                    {"match": {"content": "probatório"}}
                ],
                "minimum_should_match": 1
            }
        }
    }
]

# realiza as consultas e salva os resultados
for query_info in queries:
    search_in_elasticsearch(es, index_name, query_info["query"], query_info["description"])

print("Processo de consulta concluído.")
