from sqlalchemy import event
from sqlalchemy.engine import create_engine
import config

engine = create_engine(
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}/{config.DB_SCHEMA}"
)