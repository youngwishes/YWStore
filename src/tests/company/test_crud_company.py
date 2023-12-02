from __future__ import annotations
from typing import TYPE_CHECKING

import pytest
from fastapi import status
from src.main import YshopAPI
from src.tests.helpers import (
    make_post_request,
    get_objects_count,
    get_object,
    check_object_data,
)
from src.apps.company.models import Company

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_register_new_company_authorized(
    company_init_data: dict,
    authorized_client: AsyncClient,
    test_app: YshopAPI,
    session: AsyncSession,
):
    """
    Тест на создание новой компании авторизованным пользователем
    Проверяет:
    1. Код ответа
    2. Количество записей в БД
    3. Соответствие переданных данных с записью в базе данных
    """
    count_before = await get_objects_count(Company, session)
    url = test_app.url_path_for("register_company")
    response = await make_post_request(authorized_client, url, json=company_init_data)
    count_after = await get_objects_count(Company, session)
    obj = await get_object(Company, session)

    assert response.status_code == status.HTTP_201_CREATED
    assert count_before + 1 == count_after
    assert await check_object_data(obj=obj, data=company_init_data)


@pytest.mark.anyio
async def test_register_new_company_unauthorized(
    company_init_data: dict,
    async_client: AsyncClient,
    test_app: YshopAPI,
    session: AsyncSession,
):
    """
    Тест на создание новой компании неавторизованным пользователем
    Проверяет:
    1. Код ответа
    2. Количество записей в БД
    3. Соответствие переданных данных с записью в базе данных
    """
    count_before = await get_objects_count(Company, session)
    url = test_app.url_path_for("register_company")
    response = await make_post_request(async_client, url, json=company_init_data)
    count_after = await get_objects_count(Company, session)
    obj = await get_object(Company, session)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert count_before == count_after
    assert obj is None
