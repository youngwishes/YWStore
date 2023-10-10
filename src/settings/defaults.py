from dotenv import load_dotenv
from os import getenv

load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER")

POSTGRES_DB = getenv("POSTGRES_DB")

POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")

SQL_ECHO = True
