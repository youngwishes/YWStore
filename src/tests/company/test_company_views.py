from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from fastapi import status
from src.main import app
from src.tests.helpers import (
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
    url = app.url_path_for("register_company")
    response = await authorized_client.post(url, json=company_init_data)
    count_after = await get_objects_count(Company, session)
    obj = await get_object(Company, session)
    assert response.status_code == status.HTTP_201_CREATED
    assert count_before + 1 == count_after
    assert await check_object_data(obj=obj, data=company_init_data)
    assert obj.is_verified is False


@pytest.mark.anyio
async def test_register_company_with_exists_name(
    company_init_data: dict,
    authorized_client: AsyncClient,
    session: AsyncSession,
    create_test_company: Company,
):
    """Тест на создание новой компании, имя которой уже содержится в системе"""
    count_before = await get_objects_count(Company, session)
    url = app.url_path_for("register_company")
    response = await authorized_client.post(url, json=company_init_data)
    count_after = await get_objects_count(Company, session)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert count_before == count_after


@pytest.mark.anyio
async def test_register_new_company_unauthorized(
    company_init_data: dict,
    async_client: AsyncClient,
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
    url = app.url_path_for("register_company")
    response = await async_client.post(url, json=company_init_data)
    count_after = await get_objects_count(Company, session)
    obj = await get_object(Company, session)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert count_before == count_after
    assert obj is None


@pytest.mark.anyio
async def test_update_company(
    authorized_client: AsyncClient,
    session: AsyncSession,
    create_test_company: Company,
    update_company_data: dict,
):
    """Тест проверяет корректное обновление компании авторизованным юзером"""
    url = app.url_path_for("update_company", pk=create_test_company.id)
    response = await authorized_client.put(url, json=update_company_data)
    obj = await get_object(Company, session)
    assert response.status_code == status.HTTP_200_OK
    assert await check_object_data(obj, update_company_data)


@pytest.mark.anyio
async def test_update_company_with_exists_name(
    authorized_client: AsyncClient,
    session: AsyncSession,
    create_test_company: Company,
    random_company: Company,
    update_company_data: dict,
):
    """Тест проверяет запрет на обновление названия компании если такое уже есть в системе"""
    url = app.url_path_for("update_company", pk=create_test_company.id)
    update_company_data["name"] = random_company.name
    response = await authorized_client.put(url, json=update_company_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_update_company_unauthorized(
    async_client: AsyncClient,
    session: AsyncSession,
    create_test_company: Company,
    update_company_data: dict,
    company_init_data: dict,
):
    """Тест проверяет запрет на обновление компании неавторизованным юзером"""
    url = app.url_path_for("update_company", pk=create_test_company.id)
    response = await async_client.put(url, json=update_company_data)
    obj = await get_object(Company, session)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await check_object_data(obj, company_init_data)


@pytest.mark.anyio
async def test_partially_update_company(
    authorized_client: AsyncClient,
    session: AsyncSession,
    create_test_company: Company,
    update_partial_company_data: dict,
):
    """Тест проверяет частичное обновление компании"""
    url = app.url_path_for("update_company_partially", pk=create_test_company.id)
    response = await authorized_client.patch(url, json=update_partial_company_data)
    obj = await get_object(Company, session)
    assert response.status_code == status.HTTP_200_OK
    assert await check_object_data(obj, update_partial_company_data)


@pytest.mark.anyio
async def test_partially_update_company_with_exists_name(
    authorized_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
    update_partial_company_data: dict,
    create_test_company: Company,
):
    """Тест проверяет частичное обновление компании если имя уже существует в системе"""
    url = app.url_path_for("update_company_partially", pk=create_test_company.id)
    update_partial_company_data["name"] = random_company.name
    response = await authorized_client.patch(url, json=update_partial_company_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_partially_update_company_unauthorized(
    async_client: AsyncClient,
    session: AsyncSession,
    create_test_company: Company,
    update_partial_company_data: dict,
    company_init_data: dict,
):
    """Тест проверяет частичное обновление компании от лица не авторизированного юзера"""
    url = app.url_path_for("update_company_partially", pk=create_test_company.id)
    response = await async_client.patch(url, json=update_partial_company_data)
    obj = await get_object(Company, session)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await check_object_data(obj, company_init_data)


@pytest.mark.anyio
async def test_companies_delete(
    authorized_client: AsyncClient,
    session: AsyncSession,
    create_test_company_many: int,
):
    """Удаление всех компаний"""
    url = app.url_path_for("delete_companies")
    count_objects_before = await get_objects_count(Company, session)
    assert count_objects_before != 0
    response = await authorized_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    count_objects_after = await get_objects_count(Company, session)
    assert count_objects_after == 0


@pytest.mark.anyio
async def test_companies_delete_unauthorized(
    async_client: AsyncClient,
    session: AsyncSession,
    create_test_company_many: int,
):
    """Удаление всех компаний от лица неавторизованного юзера"""
    url = app.url_path_for("delete_companies")
    count_objects_before = await get_objects_count(Company, session)
    assert count_objects_before != 0
    response = await async_client.delete(url)
    count_objects_after = await get_objects_count(Company, session)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert count_objects_after == count_objects_before


@pytest.mark.anyio
async def test_company_delete(
    authorized_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
):
    """Проверка на удаление конкретной компании"""
    url = app.url_path_for("delete_company", pk=random_company.id)
    count_objects_before = await get_objects_count(Company, session)
    assert count_objects_before != 0
    response = await authorized_client.delete(url)
    count_objects_after = await get_objects_count(Company, session)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert count_objects_before == count_objects_after + 1


@pytest.mark.anyio
async def test_company_delete_unauthorized(
    async_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
):
    """Проверка на удаление конкретной компании от лица не авторизированного юзера"""
    url = app.url_path_for("delete_company", pk=random_company.id)
    count_objects_before = await get_objects_count(Company, session)
    assert count_objects_before != 0
    await async_client.delete(url)
    count_objects_after = await get_objects_count(Company, session)
    assert count_objects_before == count_objects_after


@pytest.mark.anyio
async def test_companies_list(
    async_client: AsyncClient,
    create_test_company_many: int,
    session: AsyncSession,
):
    """Тест проверяет вывод всех компаний по гет-запросу, должны приходить не скрытые и верифицированные компании"""
    url = app.url_path_for("companies_list")
    response = await async_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == create_test_company_many


@pytest.mark.anyio
async def test_company_detail(
    async_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
):
    """Тест на детальное представление компании"""
    url = app.url_path_for("company_detail", pk=random_company.id)
    response = await async_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert check_object_data(random_company, data=response.json())


@pytest.mark.anyio
async def test_verify_company(
    authorized_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
):
    url = app.url_path_for("verify_company", pk=random_company.id)
    assert random_company.is_verified
    response = (
        await authorized_client.patch(url, json={"is_verified": False}),
        authorized_client,
        authorized_client,
        authorized_client,
        authorized_client,
    )
    await session.refresh(random_company)

    assert response.status_code == status.HTTP_200_OK
    assert random_company.is_verified is False
