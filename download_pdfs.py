import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Função para baixar um arquivo PDF
def download_pdf(pdf_url, folder):
    try:
        pdf_name = pdf_url.split("/")[-1]
        pdf_path = os.path.join(folder, pdf_name)

        print(f"Baixando {pdf_name} no diretório {pdf_path}...")
        response = requests.get(pdf_url)
        response.raise_for_status()  # Verifica se houve erro na requisição

        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(pdf_path, 'wb') as file:
            file.write(response.content)

        print(f"PDF {pdf_name} baixado com sucesso!")
    except Exception as e:
        print(f"Erro ao baixar {pdf_url}: {str(e)}")

# Função para buscar os links de PDF em uma página
def get_pdfs_from_page(url, folder):
    try:
        print(f"Processando a página de PDFs: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Verifica se houve erro na requisição

        soup = BeautifulSoup(response.text, 'html.parser')

        # Debug: Printar o HTML da página para verificar o conteúdo
        print(soup.prettify())

        pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))

        if not os.path.exists(folder):
            os.makedirs(folder)

        for link in pdf_links:
            pdf_url = urljoin(url, link['href'])
            download_pdf(pdf_url, folder)
    except Exception as e:
        print(f"Erro ao processar a página {url}: {str(e)}")

# Função para buscar links de anos e baixar todos os PDFs
def download_all_pdfs_from_unirio(base_url, folder):
    try:
        print(f"Processando a página principal: {base_url}")
        response = requests.get(base_url)
        response.raise_for_status()  # Verifica se houve erro na requisição

        soup = BeautifulSoup(response.text, 'html.parser')

        # Debug: Printar o HTML da página principal para verificar o conteúdo
        print(soup.prettify())

        # Atualizar o seletor para encontrar os links de ano corretamente
        year_links = soup.find_all('a', href=lambda href: href and '/boletins/' in href)

        # Debug: Verificar quais links foram encontrados
        print(f"Links encontrados para ano: {[link['href'] for link in year_links]}")

        for link in year_links:
            year_url = urljoin(base_url, link['href'])
            year_text = link['href'].split('/')[-1]

            if year_text.isdigit() or '-' in year_text:
                year_folder = os.path.join(folder, year_text)
                print(f"\nProcessando ano/página: {year_text}")
                get_pdfs_from_page(year_url, year_folder)
            else:
                print(f"Ignorando link não relacionado a ano: {year_url}")
    except Exception as e:
        print(f"Erro ao processar a página principal {base_url}: {str(e)}")

# URL base da UNIRIO
base_url = 'https://www.unirio.br/boletins'
# Diretório onde os PDFs serão salvos
download_folder = './boletins'

# Baixa todos os PDFs
download_all_pdfs_from_unirio(base_url, download_folder)

print("Download completo.")
