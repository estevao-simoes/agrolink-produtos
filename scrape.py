from bs4 import BeautifulSoup
import requests
import csv
import datetime
import pandas as pd

from lib import database

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
file_name = f"products_{timestamp}.csv"


def main():
    # Enrich data with details and insert into database
    database.migrate_fresh()

    # Extrair dados
    # scrape_products_page_and_save_to_file()

    # Use pandas to insert companies into database
    print("Inserting companies into database...")
    companies = insert_unique_companies()

    # Insert products into database
    print("Inserting products into database...")
    products = insert_products(companies)

    # Scrape for product details and save to memory (dict)
    # [
    # {product_id: [
    #      {"ingredient": "ingredient_name", "quantity": "quantity", "unit": "unit"},
    #      {"ingredient": "ingredient_name", "quantity": "quantity", "unit": "unit"},
    # ]},
    # {product_id: [
    #      {"ingredient": "ingredient_name", "quantity": "quantity", "unit": "unit"},
    #      {"ingredient": "ingredient_name", "quantity": "quantity", "unit": "unit"},
    # ]},
    # ]
    print("Scraping product details...")
    product_details = scrape_product_details(products)

    # Get unique ingredients
    print("Getting unique ingredients...")
    ingredients = get_unique_ingredients(product_details)

    # Insert ingredients into database
    print("Inserting ingredients into database...")
    insert_ingredients(ingredients)

    # insert procut formulas into database
    print("Inserting product formulas into database...")
    insert_product_formulas(product_details, ingredients)

    print("Done!")


def insert_product_formulas(product_details, ingredients):
    data = []

    for product_id, details in product_details.items():
        print(f"Inserting product formula {product_id} of {len(product_details)}")

        for detail in details:
            print(f"Inserting ingredient {detail['ingredient']}")

            ingredient_id = ingredients.index(detail["ingredient"]) + 1

            data.append(
                {
                    "product_id": product_id,
                    "ingredient_id": ingredient_id,
                    "quantity": detail["quantity"],
                    "unit": detail["unit"],
                }
            )

    df = pd.DataFrame(data, columns=["product_id", "ingredient_id", "quantity", "unit"])

    df.to_sql(
        "product_formulas",
        con=database.get_engine(),
        if_exists="append",
        index=False,
        chunksize=10000,
    )


def insert_ingredients(ingredients):
    df = pd.DataFrame(ingredients, columns=["name"])

    df.to_sql(
        "ingredients",
        con=database.get_engine(),
        if_exists="append",
        index=False,
        chunksize=10000,
    )


def get_unique_ingredients(product_details):
    ingredients = []

    for product_id, details in product_details.items():
        for detail in details:
            ingredients.append(detail["ingredient"])

    ingredients = list(dict.fromkeys(ingredients))

    return ingredients


def scrape_product_details(products):
    product_details = {}

    for index, row in products.iterrows():
        print(f"Scraping product {index + 1} of {len(products)}")
        product_id = index + 1
        product_details[product_id] = scrape_product_details_page(row["url"])

    return product_details


def scrape_product_details_page(url):
    request = requests.get(f"https://www.agrolink.com.br/{url}")
    body = request.text
    soup = BeautifulSoup(body, features="html.parser")

    print(f"Scraping product details page {url}")
    table = soup.find("table", class_="table table-striped agk-cont-tb1")

    # Check if table exists

    if table is None:
        return []

    print(f"Scraping product details page {url} - table")
    table_body = table.find("tbody")

    print(f"Scraping product details page {url} - rows")
    rows = table_body.find_all("tr")

    data = []

    for row in rows:
        columns = row.find_all("td")
        ingredient = columns[0].text.strip()
        quantity = columns[1].text.strip().split(" ")[0]
        unit = columns[1].text.strip().split(" ")[1]
        data.append({"ingredient": ingredient, "quantity": quantity, "unit": unit})

    print(f"Scraping product details page {url} - done")
    return data


def insert_products(companies):
    df = pd.read_csv(file_name, header=0, usecols=["Produto", "Empresa", "URL"])

    companies.loc[companies["name"] == "Agriconnection"].index

    # df.insert(3, "company_id", df["Empresa"])

    companies = companies.reset_index()

    for index, row in companies.iterrows():
        # insert company_id into df

        df.loc[df["Empresa"] == row["name"], "company_id"] = row["index"] + 1

    df.drop("Empresa", axis=1, inplace=True)

    df.rename(columns={"Produto": "name", "URL": "url"}, inplace=True)

    df["company_id"] = df["company_id"].astype(int)

    df.to_sql(
        "products",
        con=database.get_engine(),
        if_exists="append",
        index=False,
        chunksize=10000,
    )

    return df


def insert_unique_companies():
    df = pd.read_csv(file_name, header=0, usecols=["Empresa"])

    df.rename(columns={"Empresa": "name"}, inplace=True)

    df = df.drop_duplicates(subset=["name"])

    df.to_sql(
        "companies",
        con=database.get_engine(),
        if_exists="append",
        index=False,
        chunksize=10000,
    )

    return df


def extract_companies(file):
    companies = []
    with open(file, "r", newline="") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            companies.append(row[1])

    return list(dict.fromkeys(companies))


def scrape_products_page_and_save_to_file():
    # Creates the file
    print("Creating file...")
    create_file()

    page = 1
    has_products = True

    # Para cada página, fazer uma nova requisição e ler os produtos dela
    while has_products:
        print(f"Extracting Page: {page}")
        request = requests.get(
            f"https://www.agrolink.com.br/agrolinkfito/produto/lista/{page}"
        )
        body = request.text
        soup = BeautifulSoup(body, features="html.parser")
        page_products = extract_products_from_table(soup)

        if len(page_products) == 0:
            print("Done scraping")
            has_products = False

        insert_products_to_file(page_products)
        page += 1


# Criar função para extrair dados da tabela de produtos
def extract_products_from_table(page):
    rows = page.find_all("tr", id="tr_rows")

    data = {}

    for row in rows:
        columns = row.find_all("td")
        produto = columns[0].text.strip()
        empresa = columns[2].text.strip()
        ingrediente_ativo = columns[3].text.strip()
        url = columns[4].find("a")["href"]
        data[produto] = {
            "Empresa": empresa,
            "Ingrediente Ativo": ingrediente_ativo,
            "URL": url,
        }

    return data


def create_file():
    with open(file_name, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Produto", "Empresa", "Ingrediente Ativo", "URL"])


def insert_products_to_file(products):
    with open(file_name, "a", newline="") as file:
        writer = csv.writer(file)

        for produto, info in products.items():
            writer.writerow(
                [produto, info["Empresa"], info["Ingrediente Ativo"], info["URL"]]
            )


if __name__ == "__main__":
    main()
