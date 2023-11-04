from dotenv import load_dotenv
from os import getenv

load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER")

POSTGRES_DB = getenv("POSTGRES_DB")

POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")

DB_HOST = getenv("DB_HOST")

POSTGRES_DRIVER = "postgresql+asyncpg"

DB_URL = f"{POSTGRES_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:5432/{POSTGRES_DB}"

SQL_ECHO = True
