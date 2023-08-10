import os
from lib import connection
from sqlalchemy import text

def migrate_fresh():
    print("Migrating database...")
    files = get_migration_files()
    for file in files:
        print(file)
        execute_sql_file(f"./database/migrations/{file}", connection.engine)

def get_engine():
    return connection.engine

def get_migration_files():
    return sorted(os.listdir("./database/migrations"))


def execute_sql_file(file_path, engine):
    with open(file_path, "r") as f:
        commands = f.read().split(";")

    for command in commands:
        if not command.strip():
            continue
        with engine.connect() as conn:
            conn.execute(text(command))
