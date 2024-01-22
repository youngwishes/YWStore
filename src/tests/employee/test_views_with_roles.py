from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pytest
from fastapi import status
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from src.apps.company.models import Company
from src.apps.employee.models import Employee
from src.apps.roles.enums import CompanyRoles
from src.apps.users.models import User
from src.main import app

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_add_new_employee(
    any_employee_client: AsyncClient,
    init_another_employee_data: dict,
    session: AsyncSession,
    create_test_user: User,
):
    """Тест на добавление нового пользователя в компанию"""
    url = app.url_path_for("add_employee")
    company_stmt = await session.execute(
        select(Company)
        .where(Company.id == init_another_employee_data["company_id"])
        .options(selectinload(Company.employees)),
    )
    company = company_stmt.scalar_one_or_none()
    await session.refresh(company)
    employees_count_before = len(company.employees)
    response = await any_employee_client.post(url, json=init_another_employee_data)
    await session.refresh(company)
    employees_count_after = len(company.employees)
    if create_test_user.is_member(CompanyRoles.ADMIN):
        assert response.status_code == status.HTTP_201_CREATED
        assert employees_count_before == employees_count_after - 1
    else:
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert employees_count_before == employees_count_after


@pytest.mark.anyio
async def test_get_company_employees(
    any_employee_client: AsyncClient,
    session: AsyncSession,
    active_employees: Sequence[Employee],
    create_employees_many: Sequence[Employee],
    create_test_user: User,
):
    """Тест проверяет получение пользователей из компании"""
    url = app.url_path_for(
        "get_employees",
        company_pk=active_employees[0].company_id,
    )
    response = await any_employee_client.get(url)
    if create_test_user.is_member(CompanyRoles.ADMIN):
        assert response.status_code == status.HTTP_200_OK
        for data in response.json():
            assert data["user"]["is_active"] is True
    else:
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_partial_self_update_employee_by_any_employee(
    any_employee_client: AsyncClient,
    session: AsyncSession,
    employee_with_any_role: Employee,
):
    """Тест проверяет частичное обновление данных сотрудника самим сотрудником - 200 OK"""
    telegram_new_field = "some_new_field"
    url = app.url_path_for(
        "update_employee_partially",
        company_pk=employee_with_any_role.company_id,
        user_pk=employee_with_any_role.user_id,
    )
    assert employee_with_any_role.telegram != telegram_new_field
    partial_update_data = {"telegram": telegram_new_field}
    response = await any_employee_client.patch(url, json=partial_update_data)
    assert response.status_code == status.HTTP_200_OK
    await session.refresh(employee_with_any_role)
    assert employee_with_any_role.telegram == telegram_new_field


@pytest.mark.anyio
async def test_partial_update_employee_by_any_employee(
    any_employee_client: AsyncClient,
    session: AsyncSession,
    employee_with_any_role: Employee,
    random_employee: Employee,
):
    """Тест проверяет частичное обновление данных сотрудника самим сотрудником - 200 OK, или кем-либо другим - 403"""
    telegram_new_field = "some_new_field"
    url = app.url_path_for(
        "update_employee_partially",
        company_pk=random_employee.company_id,
        user_pk=random_employee.user_id,
    )
    assert employee_with_any_role.telegram != telegram_new_field
    partial_update_data = {"telegram": telegram_new_field}
    response = await any_employee_client.patch(url, json=partial_update_data)
    if random_employee.user_id == employee_with_any_role.user_id:
        assert response.status_code == status.HTTP_200_OK
        await session.refresh(employee_with_any_role)
        assert employee_with_any_role.telegram == telegram_new_field
    else:
        assert response.status_code == status.HTTP_403_FORBIDDEN
        await session.refresh(employee_with_any_role)
        assert employee_with_any_role.telegram != telegram_new_field
