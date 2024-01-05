from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pytest
from fastapi import status
from sqlalchemy import select

from src.apps.users.models import User
from src.main import app
from src.tests import defaults
from src.tests.helpers import get_objects_count, get_object, check_object_data

if TYPE_CHECKING:
    from httpx import AsyncClient
    from src.main import YWStoreAPI
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_register_view(
    async_client: AsyncClient,
    get_test_user_data: dict,
    session: AsyncSession,
):
    """Тест на регистрацию пользователя от имени неавторизированного пользователя"""
    users_count_before = await get_objects_count(User, session)
    user_stmt = await session.execute(
        select(User).where(User.email == get_test_user_data["email"]),
    )
    assert user_stmt.scalar_one_or_none() is None

    url = app.url_path_for("register_user")
    response = await async_client.post(url, json=get_test_user_data)
    users_count_after = await get_objects_count(User, session)

    assert response.status_code == status.HTTP_201_CREATED
    assert users_count_before + 1 == users_count_after
    user_object = await get_object(User, session)
    assert await check_object_data(user_object, get_test_user_data)
    assert user_object.is_verified is False


@pytest.mark.anyio
async def test_auth_view(
    async_client: AsyncClient,
    test_app: YWStoreAPI,
    create_test_user: User,
    session: AsyncSession,
):
    """Тест на авторизацию пользователя (в том числе проставление поля last_login)"""
    assert create_test_user.last_login is None

    url = test_app.url_path_for("auth:jwt.login")
    response = await async_client.post(
        url,
        data={
            "username": defaults.TEST_USER_EMAIL,
            "password": defaults.TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"]

    await session.refresh(create_test_user)
    assert create_test_user.last_login


@pytest.mark.anyio
async def test_get_user_by_authorized(
    authorized_client: AsyncClient,
    get_test_user_data: dict,
):
    """Тест на получение информации о текущем пользователе от авторизированного пользователя"""
    url = app.url_path_for("get_user")
    response = await authorized_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == get_test_user_data["email"]


@pytest.mark.anyio
async def test_get_user_by_unauthorized(async_client: AsyncClient):
    """Тест на получение информации о текущем пользователе от неавторизированного пользователя"""
    url = app.url_path_for("get_user")
    response = await async_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_delete_user_by_authorized(
    authorized_client: AsyncClient,
    create_test_user: User,
    session: AsyncSession,
):
    "Тест на удаление пользователя от имени авторизированного пользователя"
    users_count_before = await get_objects_count(User, session)

    url = app.url_path_for("user_delete")
    response = await authorized_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    users_count_after = await get_objects_count(User, session)
    assert users_count_after == users_count_before - 1
    user_stmt = await session.execute(
        select(User).where(User.id == create_test_user.id),
    )
    assert user_stmt.scalar_one_or_none() is None


@pytest.mark.anyio
async def test_delete_user_by_unauthorized(
    async_client: AsyncClient,
    session: AsyncSession,
):
    """Тест на удаление пользователя от имени неавторизированного пользователя"""
    url = app.url_path_for("user_delete")
    response = await async_client.delete(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_edit_user_by_authorized(
    authorized_client: AsyncClient,
    get_test_user_data: dict,
    session: AsyncSession,
):
    """Тест на обновление данных пользователя от имени авторизованного пользователя"""
    url = app.url_path_for("user_edit")
    to_change_email = "example_user_email_test1@example.com"
    get_test_user_data["email"] = to_change_email
    user_stmt = await session.execute(
        select(User).where(User.email == to_change_email),
    )
    assert user_stmt.unique().scalar_one_or_none() is None
    response = await authorized_client.patch(url, json=get_test_user_data)

    assert response.status_code == status.HTTP_200_OK
    user_stmt = await session.execute(
        select(User).where(User.email == to_change_email),
    )
    assert user_stmt.unique().scalar_one_or_none() is not None


@pytest.mark.anyio
async def test_edit_user_with_exist_email_by_authorized(
    authorized_client: AsyncClient,
    get_test_user_data: dict,
    session: AsyncSession,
    create_test_users: Sequence[User],
):
    """Тест обновления данных пользователя на существующие от имени авторизированного пользователя"""
    url = app.url_path_for("user_edit")
    get_test_user_data["email"] = create_test_users[1].email
    response = await authorized_client.patch(url, json=get_test_user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user_stmt = await session.execute(
        select(User).where(User.email == get_test_user_data["email"]),
    )
    user = user_stmt.unique().scalar_one_or_none()
    assert user is not None
    assert user.email != create_test_users[0].email


@pytest.mark.anyio
async def test_edit_user_by_unauthorized(
    async_client: AsyncClient,
    get_test_user_data: dict,
    session: AsyncSession,
):
    """Тест на обновление данных пользователя от имени не авторизованного пользователя"""
    url = app.url_path_for("user_edit")
    to_change_email = "example_user_email_test1@example.com"
    get_test_user_data["email"] = to_change_email
    user_stmt = await session.execute(
        select(User).where(User.email == to_change_email),
    )
    assert user_stmt.unique().scalar_one_or_none() is None
    response = await async_client.patch(url, json=get_test_user_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    user_stmt = await session.execute(
        select(User).where(User.email == to_change_email),
    )
    assert user_stmt.unique().scalar_one_or_none() is None
