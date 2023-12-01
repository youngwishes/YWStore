from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from fastapi import status
from src.tests.helpers import make_post_request, get_objects_count, get_object
from src.apps.company.models import Company

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_register_new_company_status(
    company_init_data: dict,
    async_client: AsyncClient,
    test_app,
):
    """Проверяет код ответа когда создается новая компания"""
    url = test_app.url_path_for("register_company")
    response = await make_post_request(async_client, url, json=company_init_data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_register_new_company_count(
    session: AsyncSession,
    company_init_data: dict,
    async_client: AsyncClient,
    test_app,
):
    """Проверяет количество записей в БД"""
    url = test_app.url_path_for("register_company")
    count_before = await get_objects_count(Company, session)
    await make_post_request(async_client, url, json=company_init_data)
    count_after = await get_objects_count(Company, session)
    assert count_before + 1 == count_after


@pytest.mark.anyio
async def test_register_new_company_data(
    session: AsyncSession,
    company_init_data: dict,
    async_client: AsyncClient,
    test_app,
):
    """Проверяет корректность создания записи в  БД"""
    url = test_app.url_path_for("register_company")
    response = await make_post_request(async_client, url, json=company_init_data)
    obj = await get_object(Company, session)
    assert obj.id == response.json()["id"]
    assert obj.name == response.json()["name"]
    assert obj.fact_address == response.json()["fact_address"]
    assert obj.jur_address == response.json()["jur_address"]
