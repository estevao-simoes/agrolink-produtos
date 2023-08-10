from sqlalchemy.engine import create_engine
from lib import config

engine = create_engine(
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
)