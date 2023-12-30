from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from fastapi import status
from src.tests import defaults
from src.tests.helpers import get_objects_count, get_object, check_object_data
from src.core.users.models import User
from src.main import app

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
    users_count_do = await get_objects_count(User, session)

    url = app.url_path_for("register_user")
    response = await async_client.post(url, json=get_test_user_data)
    users_count_after = await get_objects_count(User, session)
    user_object: User = await get_object(User, session)

    assert response.status_code == status.HTTP_201_CREATED
    assert users_count_do + 1 == users_count_after
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
