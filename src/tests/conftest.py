from __future__ import annotations
from typing import AsyncGenerator, TYPE_CHECKING

import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from src.main import app
from src.tests import defaults
from src.core.config import get_settings
from src.core.sql.database import Base, get_session

from httpx import AsyncClient

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine
    from src.main import YshopAPI

settings = get_settings(db_only=True)

async_engine = create_async_engine(settings.sqlalchemy_db_uri)


@pytest.fixture(scope="session")
async def create_test_db() -> AsyncGenerator[AsyncEngine, None]:
    async with async_engine.connect() as connection:
        await connection.execute(text("COMMIT;"))
        await connection.execute(text("CREATE DATABASE test_db;"))
    yield create_async_engine(defaults.SQLALCHEMY_DATABASE_TEST_URI)
    async with async_engine.connect() as connection:
        await connection.execute(text("COMMIT"))
        await connection.execute(text("DROP DATABASE test_db WITH (FORCE);"))


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def bind(create_test_db: AsyncEngine) -> AsyncGenerator[AsyncEngine, None]:
    async with create_test_db.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield async_engine
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()


@pytest.fixture(scope="session")
def async_session_class(bind: AsyncEngine) -> sessionmaker[AsyncSession]:
    return sessionmaker(
        bind=bind,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture(scope="session")
def test_app(async_session_class: sessionmaker[AsyncSession]) -> YshopAPI:
    async def get_test_session():
        async with async_session_class() as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    return app


@pytest.fixture
async def session(async_session_class: sessionmaker[AsyncSession]) -> AsyncSession:
    async with async_session_class() as session:
        await session.begin()

        yield session

        await session.rollback()

        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE FROM {table.name};"))
            await session.commit()


@pytest.fixture
def async_client(test_app: YshopAPI) -> AsyncClient:
    return AsyncClient(app=test_app, base_url=defaults.BASE_API_URL)
