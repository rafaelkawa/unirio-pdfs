# ETL de Boletins da UNIRIO com Elasticsearch

Este projeto realiza a indexação de arquivos PDF e permite a busca através dos conteúdos desses arquivos usando Elasticsearch. Além disso, os resultados das buscas são salvos em arquivos de texto.

## Requisitos

- **Python 3.6+**
- **Elasticsearch** (versão 7.10.1)
- **Kibana** (versão 7.10.1)
- **Docker** (para rodar Elasticsearch e Kibana em containers)

## Configuração do Ambiente

### 1. Configuração com Docker

Para simplificar a configuração, o Docker foi utilizado para rodar o Elasticsearch e Kibana. 

1. **Instale o Docker** se ainda não estiver instalado.

2. **Inicie Elasticsearch e Kibana usando Docker:**

    ```bash
    docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.10.1
    docker run -d --name kibana -p 5601:5601 --link elasticsearch:elasticsearch kibana:7.10.1
    ```

3. **Acesse os serviços:**

    - Elasticsearch: `http://localhost:9200`
    - Kibana: `http://localhost:5601`

### 2. Instalação das Dependências

1. **Crie e ative um ambiente virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Para Linux/Mac
    venv\Scripts\activate  # Para Windows
    ```

2. **Instale as dependências necessárias:**

    ```bash
    pip install -r requirements.txt
    ```

### 3. Processamento e Indexação dos PDFs

1. **Baixar os PDFs:**

    Execute o script `download_pdfs.py` para baixar os PDFs da UNIRIO e salvá-los na pasta `boletins`:

    ```bash
    python download_pdfs.py
    ```

2. **Indexar o conteúdo dos PDFs no Elasticsearch:**

    Execute o script `index_documents.py` para extrair o texto dos PDFs e indexá-los:

    ```bash
    python index_documents.py
    ```

3. **Realizar buscas:**

    Execute o script `main.py` para realizar buscas e salvar os resultados:

    ```bash
    python main.py
    ```

    O script gera arquivos de texto na pasta `resultados` com os detalhes das buscas realizadas.

### 4. Visualização dos Resultados no Kibana

1. **Acesse o Kibana em** `http://localhost:5601`.

2. **Explore os dados:**

    - Vá para a aba **"Discover"** para visualizar e explorar os dados indexados.
    - Criar **visualizações**/**dashboards** para analise de dados.

### Alterações no Código

- **Para modificar as buscas em `main.py`:** Edite a lista `queries` com novas consultas. Cada consulta deve ter uma `description` e um `query`. Ajuste o formato das consultas conforme necessário para suas buscas específicas.

### Estrutura dos Diretórios

- **`boletins/`**: Pasta onde os PDFs são armazenados.
- **`resultados/`**: Pasta onde os resultados das buscas são salvos em arquivos de texto.


