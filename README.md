# agrolink-produtos
ETL para consumir e estruturar dados de produtos do site Agrolink

## Ambiente
- `Python 3.9.17`
- `python -m venv`

## Rodando
1. `python venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`
5. Edite a .env apontando para um banco de dados
6. `python scrape.py`
