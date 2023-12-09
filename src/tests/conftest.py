from __future__ import annotations
from typing import AsyncGenerator, TYPE_CHECKING

import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.pool import NullPool

from src.apps.company.enums import CompanyType
from src.apps.company.models import Company
from src.main import app
from src.tests import defaults
from src.core.config import get_settings
from src.core.sql.database import Base, get_session
from src.core.users.models import User
from src.core.users.schemas import UserCreate

from httpx import AsyncClient
from src.core.users.manager import UserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine
    from src.main import YStore

settings = get_settings(db_only=True)
async_engine_main = create_async_engine(settings.sqlalchemy_db_uri, poolclass=NullPool)
async_engine_test = create_async_engine(defaults.SQLALCHEMY_DATABASE_TEST_URI)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine]:
    async with async_engine_main.connect() as connection:
        await connection.execute(text("COMMIT;"))
        await connection.execute(text(f"CREATE DATABASE {defaults.TEST_DB_NAME};"))
    async with async_engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield async_engine_test
    await async_engine_test.dispose()
    async with async_engine_main.connect() as connection:
        await connection.execute(text("COMMIT;"))
        await connection.execute(text(f"DROP DATABASE {defaults.TEST_DB_NAME};"))


@pytest.fixture(scope="session")
def async_session_class(engine: AsyncEngine) -> sessionmaker[AsyncSession]:
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)  # type: ignore[call-arg]


@pytest.fixture(scope="session")
def test_app(async_session_class: sessionmaker[AsyncSession]) -> YStore:
    async def get_test_session():
        async with async_session_class() as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    return app


@pytest.fixture(scope="function", autouse=True)
async def session(
    async_session_class: sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_class() as session:
        yield session
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE {table.name} CASCADE;"))
        await session.commit()


@pytest.fixture
async def get_test_user_db(
    session: AsyncSession,
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)  # type: ignore[call-arg]


@pytest.fixture
async def get_test_user_manager(
    get_test_user_db: SQLAlchemyUserDatabase,
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(get_test_user_db)


@pytest.fixture
async def async_client(test_app: YStore) -> AsyncClient:
    async with AsyncClient(app=test_app, base_url=defaults.HOST_URL) as client:
        yield client


@pytest.fixture
async def authorized_client(
    async_client: AsyncClient,
    create_test_user: User,
    get_test_user_data: dict,
    test_app: YStore,
) -> AsyncGenerator[AsyncClient, None]:
    url = app.url_path_for("auth:jwt.login")
    credentials = {
        "username": get_test_user_data.get("email"),
        "password": get_test_user_data.get("password"),
    }
    response = await async_client.post(url, data=credentials)
    access_token = response.json().get("access_token")
    async_client.headers = {"Authorization": f"Bearer {access_token}"}
    yield async_client


@pytest.fixture
async def superuser_client(
    authorized_client: AsyncClient,
    create_test_user: User,
    session: AsyncSession,
):
    create_test_user.is_superuser = True
    session.add(create_test_user)
    await session.commit()
    return authorized_client


@pytest.fixture
def get_test_user_data() -> dict:
    return {
        "email": defaults.TEST_USER_EMAIL,
        "first_name": defaults.TEST_USER_FIRST_NAME,
        "last_name": defaults.TEST_USER_LAST_NAME,
        "middle_name": defaults.TEST_USER_MIDDLE_NAME,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "password": defaults.TEST_USER_PASSWORD,
    }


@pytest.fixture
async def create_test_user(
    session: AsyncSession,
    get_test_user_data: dict,
    get_test_user_manager: UserManager,
) -> User:
    create_user_schema = UserCreate(**get_test_user_data)
    user = await get_test_user_manager.create(create_user_schema)
    return user


@pytest.fixture
def company_init_data():
    return {
        "name": "Test",
        "director_fullname": "Test",
        "type": CompanyType.LLC,
        "jur_address": {"Country": "Russian Federation"},
        "fact_address": {"Country": "Russian Federation"},
    }


@pytest.fixture
async def create_test_company(
    company_init_data: dict,
    session: AsyncSession,
) -> Company:
    company = Company(**company_init_data, is_verified=True, is_hidden=False)  # type: ignore[call-arg]
    session.add(company)
    await session.commit()
    await session.refresh(company)
    yield company
