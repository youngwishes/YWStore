from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.settings import defaults
from sqlalchemy import URL, create_engine

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = URL.create(
    drivername=defaults.POSTGRES_DRIVER,
    username=defaults.POSTGRES_USER,
    password=defaults.POSTGRES_PASSWORD,
    host=defaults.DB_HOST,
    database=defaults.POSTGRES_DB,
)

engine = AsyncEngine(
    create_engine(SQLALCHEMY_DATABASE_URL, echo=defaults.SQL_ECHO, future=True),
)


async def get_db() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
