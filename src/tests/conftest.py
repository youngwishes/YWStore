from __future__ import annotations

from copy import copy
from typing import AsyncGenerator, TYPE_CHECKING, Sequence

import pytest
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text, select

from src.apps.company.enums import CompanyType
from src.apps.company.models import Company
from src.apps.employee.models import Employee
from src.apps.roles.enums import CompanyRoles
from src.core.config import get_settings
from src.core.sql.database import Base, get_session
from src.core.users.manager import UserService
from src.core.users.models import User, Role
from src.core.users.schemas import UserCreate
from src.main import app
from src.tests import defaults

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine
    from src.main import YWStoreAPI

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
    return sessionmaker(  # type: ignore[call-arg]
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture(scope="session")
def test_app(async_session_class: sessionmaker[AsyncSession]) -> YWStoreAPI:
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
async def get_test_user_service(
    get_test_user_db: SQLAlchemyUserDatabase,
) -> AsyncGenerator[UserService, None]:
    yield UserService(get_test_user_db)


@pytest.fixture
async def async_client(test_app: YWStoreAPI) -> AsyncClient:
    async with AsyncClient(app=test_app, base_url=defaults.HOST_URL) as client:
        yield client


@pytest.fixture
async def authorized_client(
    async_client: AsyncClient,
    create_test_user: User,
    get_test_user_data: dict,
    test_app: YWStoreAPI,
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
def get_test_users_data(get_test_user_data) -> list[dict]:
    users_schemas = []
    for i in map(str, range(1, 11)):
        schema = copy(get_test_user_data)
        schema.update(
            {
                "email": i + get_test_user_data["email"],
                "first_name": get_test_user_data["first_name"] + i,
                "is_active": False if int(i) % 2 == 0 else True,
                "password": get_test_user_data["password"] + i,
            },
        )
        users_schemas.append(schema)
    return users_schemas


@pytest.fixture
async def create_test_user(
    session: AsyncSession,
    get_test_user_data: dict,
    get_test_user_service: UserService,
) -> User:
    create_user_schema = UserCreate(**get_test_user_data)
    user = await get_test_user_service.create(create_user_schema)
    return user


@pytest.fixture
def init_employee_data(
    create_test_company: Company,
    create_test_user: User,
):
    return {
        "company_id": create_test_company.id,
        "user_id": create_test_user.id,
        "vk": "string",
        "telegram": "string",
        "extra_data": "string",
        "is_active": True,
        "phone_number": "string",
    }


@pytest.fixture
async def create_test_users(
    get_test_users_data: list[dict],
    get_test_user_service: UserService,
) -> Sequence[User]:
    create_users_schemas = [
        UserCreate(**test_user_data) for test_user_data in get_test_users_data
    ]
    users = [
        await get_test_user_service.create(user_schema)
        for user_schema in create_users_schemas
    ]
    return users


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


@pytest.fixture
async def create_company_roles(session: AsyncSession) -> None:
    for role_name in CompanyRoles.list():
        role = Role(name=role_name)  # type: ignore[call-arg]
        session.add(role)
    await session.commit()


@pytest.fixture(params=CompanyRoles.list())
async def user_with_any_role(
    request,
    create_test_user: User,
    session: AsyncSession,
    create_company_roles,
) -> User:
    role = await session.execute(select(Role).where(Role.name == request.param))
    create_test_user.roles.append(role.unique().scalar_one())
    session.add(create_test_user)
    await session.commit()
    return create_test_user


@pytest.fixture
async def employee_with_any_role(
    user_with_any_role: User,
    init_employee_data: dict,
    session: AsyncSession,
):
    init_employee_data["user_id"] = user_with_any_role.id
    employee = Employee(**init_employee_data)
    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


@pytest.fixture
async def any_employee_client(
    employee_with_any_role: Employee,
    get_test_user_data: dict,
    async_client: AsyncClient,
):
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
async def user_admin(
    create_test_user: User,
    session: AsyncSession,
    create_company_roles,
) -> User:
    admin_role = await session.execute(
        select(Role).where(Role.name == CompanyRoles.ADMIN),
    )
    create_test_user.roles.append(admin_role.unique().scalar_one_or_none())
    return create_test_user


@pytest.fixture
async def employee_admin(
    user_admin: User,
    init_employee_data: dict,
    session: AsyncSession,
    create_test_company: Company,
) -> Employee:
    init_employee_data["user_id"] = user_admin.id
    init_employee_data["company_id"] = create_test_company.id
    employee = Employee(**init_employee_data)  # type: ignore[call-args]
    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


@pytest.fixture
async def admin_employee_client(
    async_client: AsyncClient,
    employee_admin: Employee,
    get_test_user_data: dict,
):
    url = app.url_path_for("auth:jwt.login")
    credentials = {
        "username": get_test_user_data.get("email"),
        "password": get_test_user_data.get("password"),
    }
    response = await async_client.post(url, data=credentials)
    access_token = response.json().get("access_token")
    async_client.headers = {"Authorization": f"Bearer {access_token}"}
    yield async_client
