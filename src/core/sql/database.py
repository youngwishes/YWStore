from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.settings import defaults
from sqlalchemy import URL
from sqlalchemy.exc import DatabaseError

SQLModel = declarative_base()

SQLALCHEMY_DATABASE_URL = URL.create(
    drivername=defaults.POSTGRES_DRIVER,
    username=defaults.POSTGRES_USER,
    password=defaults.POSTGRES_PASSWORD,
    host=defaults.DB_HOST,
    database=defaults.POSTGRES_DB,
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=defaults.SQL_ECHO,
)

AsyncSessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
    class_=AsyncSession,
)


async def get_db() -> AsyncSession:
    db = AsyncSessionLocal()
    try:
        yield db
    except DatabaseError as exc:
        # TODO заменить на нормальное логирование
        print(f"Python says:: {exc}")
    finally:
        await db.close()
