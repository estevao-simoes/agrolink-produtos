from bs4 import BeautifulSoup
import requests
from math import ceil
import csv
import datetime

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
file_name = f"products_{timestamp}.csv"

def main():

    # Creates the file
    create_file()

    # Buscar a primeira página de produtos
    request = requests.get("https://www.agrolink.com.br/agrolinkfito/produto/lista/1")
    body = request.text

    # Parseando o HTML para o Beatiful soup
    soup = BeautifulSoup(body, features="html.parser")

    # Buscar o total de registros e quantidade de páginas (total de registros / quantidade por página)
    table_description = soup.find_all('small')[6]

    amount_per_page = table_description.text.split(' ')[-3:][0]

    total_per_page = table_description.text.split(' ')[-1]
    total_per_page = total_per_page.replace('.', '')

    total_pages = ceil(int(total_per_page) / int(amount_per_page))

    print("Amount per page:", amount_per_page)
    print("Total pages:", total_pages)
    print("Total products:", total_per_page)
    print("=" * 100)

    # Ler dados de produtos da primeira página
    first_page_products = extract_products_from_table(soup)
    insert_products_to_file(first_page_products)

    # Para cada página, fazer uma nova requisição e ler os produtos dela
    for i in range(1, total_pages + 1):
        print(f"Extracting Page: {i}")
        request = requests.get(f"https://www.agrolink.com.br/agrolinkfito/produto/lista/{i}")
        body = request.text
        soup = BeautifulSoup(body, features="html.parser")
        page_products = extract_products_from_table(soup)
        insert_products_to_file(page_products)    

# Criar função para extrair dados da tabela de produtos
def extract_products_from_table(page):
    rows = page.find_all('tr', id='tr_rows')

    data = {}

    for row in rows:
        columns = row.find_all('td')
        produto = columns[0].text.strip()
        empresa = columns[2].text.strip()
        ingrediente_ativo = columns[3].text.strip()
        url = columns[4].find('a')['href']
        data[produto] = {'Empresa': empresa, 'Ingrediente Ativo': ingrediente_ativo, 'URL': url}
    
    return data

def create_file():
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Produto', 'Empresa', 'Ingrediente Ativo', 'URL'])

def insert_products_to_file(products):
    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)

        for produto, info in products.items():
            writer.writerow([produto, info['Empresa'], info['Ingrediente Ativo'], info['URL']])

if __name__ == "__main__":
    main()