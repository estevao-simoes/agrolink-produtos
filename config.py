import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "root")
DB_NAME = os.environ.get("DB_NAME", "agrolink")
DB_HOST = os.environ.get("DB_HOST", "localhost")