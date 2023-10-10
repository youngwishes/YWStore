from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.settings import defaults
from sqlalchemy import URL

SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql",
    username=defaults.POSTGRES_USER,
    password=defaults.POSTGRES_PASSWORD,
    host="localhost",
    database=defaults.POSTGRES_DB,
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"connect_timeout": 10},
    echo=defaults.SQL_ECHO,
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()
