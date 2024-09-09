# Projeto de Indexação e Busca de Boletins

Este projeto é uma aplicação que baixa boletins em formato PDF de uma página da UNIRIO, extrai o texto dos PDFs, indexa o conteúdo em Elasticsearch e realiza buscas utilizando consultas complexas. Além disso, inclui instruções para visualizar os dados usando Kibana.

## Pré-requisitos

- [Python 3.x](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Estrutura do Projeto

- `download_pdfs.py`: Script para baixar PDFs das páginas da UNIRIO.
- `main.py`: Script para processar e indexar os PDFs no Elasticsearch e realizar buscas.
- `requirements.txt`: Lista de dependências do Python.

## Instalação

### 1. Clonar o Repositório

Clone o repositório para o seu ambiente local:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Instalar Dependências

Crie e ative um ambiente virtual (opcional, mas recomendado) e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate  # No Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Executando o Projeto

### 1. Configurar Elasticsearch e Kibana com Docker

Crie um arquivo `docker-compose.yml` com o seguinte conteúdo:

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.6.3
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - ELASTIC_PASSWORD=changeme
    ports:
      - "9200:9200"
    networks:
      - es-net

  kibana:
    image: docker.elastic.co/kibana/kibana:8.6.3
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=elastic
      - ELASTICSEARCH_PASSWORD=changeme
    ports:
      - "5601:5601"
    networks:
      - es-net

networks:
  es-net:
    driver: bridge
```

Inicie os containers do Elasticsearch e Kibana:

```bash
docker-compose up -d
```

### 2. Baixar os PDFs

Execute o script `download_pdfs.py` para baixar os PDFs da página da UNIRIO:

```bash
python download_pdfs.py
```

### 3. Processar e Indexar os PDFs

Depois de baixar os PDFs, execute o script `main.py` para extrair o texto, indexar os documentos no Elasticsearch e realizar as buscas:

```bash
python main.py
```

## Visualizando Dados com Kibana

1. Abra o Kibana no navegador: [http://localhost:5601](http://localhost:5601).

2. Configure o índice no Kibana:
   - Vá para `Stack Management` > `Kibana` > `Index Patterns`.
   - Clique em `Create index pattern`.
   - Defina o padrão do índice como `boletins` e clique em `Next step`.
   - Selecione um campo de data (opcional) e clique em `Create index pattern`.

3. Realize buscas e visualize os dados:
   - Vá para `Discover` para visualizar os dados indexados.
   - Use `Visualize` e `Dashboard` para criar visualizações e dashboards com os dados indexados.

## Arquivo `requirements.txt`

Certifique-se de que o arquivo `requirements.txt` contém as seguintes dependências:

```
requests
beautifulsoup4
pypdf2
elasticsearch
```

## Notas

- O Elasticsearch e o Kibana estão configurados para rodar em modo de nó único para desenvolvimento. Para ambientes de produção, considere configurações de cluster.
- Os scripts assumem que a estrutura dos diretórios para PDFs será organizada com base nos anos ou diretórios similares.

## Contribuições

Sinta-se à vontade para contribuir com o projeto. Envie pull requests ou abra issues para sugestões e melhorias.

---

