from __future__ import annotations
from typing import TYPE_CHECKING

import pytest
from fastapi import status
from sqlalchemy import select

from src.apps.roles.enums import CompanyRoles
from src.apps.users.models import User
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
async def test_register_new_company_by_any_employee(
    company_init_data: dict,
    any_employee_client: AsyncClient,
    session: AsyncSession,
):
    """Тест проверяет создание новой компании от лица всех возможных ролей юзера"""
    count_before = await get_objects_count(Company, session)
    url = app.url_path_for("register_company")
    response = await any_employee_client.post(url, json=company_init_data)
    count_after = await get_objects_count(Company, session)
    assert response.status_code == status.HTTP_403_FORBIDDEN
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
    any_employee_client: AsyncClient,
    session: AsyncSession,
    create_test_company: Company,
    update_company_data: dict,
    create_test_user: User,
):
    """Тест проверяет корректное обновление компании юзером с ролью ADMIN"""
    url = app.url_path_for("update_company", company_pk=create_test_company.id)
    response = await any_employee_client.put(url, json=update_company_data)
    obj = await get_object(Company, session)
    if create_test_user.is_member(CompanyRoles.ADMIN):
        assert response.status_code == status.HTTP_200_OK
        assert await check_object_data(obj, update_company_data)
    else:
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not await check_object_data(obj, update_company_data)


@pytest.mark.anyio
async def test_partially_update_company(
    any_employee_client: AsyncClient,
    session: AsyncSession,
    create_test_company: Company,
    update_partial_company_data: dict,
    create_test_user: User,
):
    """Тест проверяет частичное обновление компании"""
    url = app.url_path_for(
        "update_company_partially",
        company_pk=create_test_company.id,
    )
    response = await any_employee_client.patch(url, json=update_partial_company_data)
    obj = await get_object(Company, session)
    if create_test_user.is_member(CompanyRoles.ADMIN):
        assert response.status_code == status.HTTP_200_OK
        assert await check_object_data(obj, update_partial_company_data)
    else:
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not await check_object_data(obj, update_partial_company_data)


@pytest.mark.anyio
async def test_companies_delete_by_any_user(
    any_employee_client: AsyncClient,
    session: AsyncSession,
    create_test_company_many: int,
):
    """Удаление всех компаний от лица всех возможных ролей юзера"""
    url = app.url_path_for("delete_companies")
    count_objects_before = await get_objects_count(Company, session)
    assert count_objects_before != 0
    response = await any_employee_client.delete(url)
    count_objects_after = await get_objects_count(Company, session)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert count_objects_after == count_objects_before


@pytest.mark.anyio
async def test_company_delete_by_any_user(
    any_employee_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
):
    """Проверка на удаление конкретной компании от всех возможных ролей юзера"""
    url = app.url_path_for("delete_company", company_pk=random_company.id)
    count_objects_before = await get_objects_count(Company, session)
    assert count_objects_before != 0
    response = await any_employee_client.delete(url)
    count_objects_after = await get_objects_count(Company, session)
    assert count_objects_before == count_objects_after
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_verify_company_authorized(
    any_employee_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
):
    url = app.url_path_for("verify_company", company_pk=random_company.id)
    assert random_company.is_verified is True
    response = await any_employee_client.patch(url, json={"is_verified": False})
    await session.refresh(random_company)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert random_company.is_verified is True


@pytest.mark.anyio
async def test_hide_company_authorized(
    any_employee_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
):
    """Тест на скрытие компании из системы"""
    assert random_company.is_hidden is False
    url = app.url_path_for("hide_company", company_pk=random_company.id)
    response = await any_employee_client.patch(url, json={"is_hidden": True})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    await session.refresh(random_company)
    assert random_company.is_hidden is False


@pytest.mark.anyio
async def test_partially_update_company_by_admin_in_another_company(
    admin_employee_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
    update_partial_company_data: dict,
    create_test_user: User,
):
    """Тест проверяет частичное обновление компании админом в которой он не является сотрудником."""
    assert CompanyRoles.ADMIN == create_test_user.roles[0].name
    url = app.url_path_for("update_company_partially", company_pk=random_company.id)
    response = await admin_employee_client.patch(url, json=update_partial_company_data)
    obj = await session.execute(select(Company).where(Company.id == random_company.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not await check_object_data(
        obj.unique().scalar_one_or_none(),
        update_partial_company_data,
    )


@pytest.mark.anyio
async def test_update_company_by_admin_in_another_company(
    admin_employee_client: AsyncClient,
    session: AsyncSession,
    random_company: Company,
    update_company_data: dict,
    create_test_user: User,
):
    """Тест проверяет обновление компании админом в которой он не является сотрудником."""
    assert CompanyRoles.ADMIN == create_test_user.roles[0].name
    url = app.url_path_for("update_company", company_pk=random_company.id)
    response = await admin_employee_client.put(url, json=update_company_data)
    obj = await session.execute(select(Company).where(Company.id == random_company.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not await check_object_data(
        obj.unique().scalar_one_or_none(),
        update_company_data,
    )
