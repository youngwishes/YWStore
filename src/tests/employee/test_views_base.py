from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi import status
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from src.apps.company.models import Company
from src.apps.employee.models import Employee
from src.apps.employee.schemas import EmployeeIn, EmployeeOptional

from src.main import app
from src.tests.helpers import check_object_data

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_delete_employee_superuser(
    async_client: AsyncClient,
    session: AsyncSession,
    create_employee: Employee,
    superuser_client: AsyncClient,
):
    """Тест проверяет мягкое удаление пользователя из компании от имени супер пользователя"""
    employee_request = await session.execute(
        select(Employee).where(Employee.user_id == create_employee.user_id),
    )
    employee_do = employee_request.unique().scalar_one_or_none()
    assert employee_do.is_active is True

    url = app.url_path_for(
        "delete_employee",
        company_pk=create_employee.company_id,
        user_pk=create_employee.user_id,
    )
    response = await superuser_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.refresh(employee_do)
    employee_request = await session.execute(
        select(Employee).where(Employee.user_id == create_employee.user_id),
    )
    employee_after = employee_request.unique().scalar_one_or_none()
    assert employee_after.is_active is False


@pytest.mark.anyio
async def test_delete_employee_authorized(
    async_client: AsyncClient,
    session: AsyncSession,
    create_employee: Employee,
    authorized_client: AsyncClient,
):
    """Тест проверяет мягкое удаление пользователя из компании от имени авторизированного клиента"""

    employee_request = await session.execute(
        select(Employee).where(Employee.user_id == create_employee.user_id),
    )
    employee_do = employee_request.unique().scalar_one_or_none()
    assert employee_do.is_active is True

    url = app.url_path_for(
        "delete_employee",
        company_pk=create_employee.company_id,
        user_pk=create_employee.user_id,
    )
    response = await authorized_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await session.refresh(employee_do)
    employee_request = await session.execute(
        select(Employee).where(Employee.user_id == create_employee.user_id),
    )
    employee_after = employee_request.unique().scalar_one_or_none()
    assert employee_after.is_active is True


@pytest.mark.anyio
async def test_delete_employee_unauthorized(
    async_client: AsyncClient,
    session: AsyncSession,
    create_employee: Employee,
):
    """Тест проверяет мягкое удаление пользователя из компании от имени неавторизированного клиента"""

    employee_request = await session.execute(
        select(Employee).where(Employee.user_id == create_employee.user_id),
    )
    employee_do = employee_request.unique().scalar_one_or_none()
    assert employee_do.is_active is True

    url = app.url_path_for(
        "delete_employee",
        company_pk=create_employee.company_id,
        user_pk=create_employee.user_id,
    )
    response = await async_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await session.refresh(employee_do)
    employee_request = await session.execute(
        select(Employee).where(Employee.user_id == create_employee.user_id),
    )
    employee_after = employee_request.unique().scalar_one_or_none()
    assert employee_after.is_active is True


@pytest.mark.anyio
async def test_partial_update_employee_by_superuser(
    superuser_client: AsyncClient,
    session: AsyncSession,
    create_employee: Employee,
    random_employee: Employee,
):
    """Тест проверяет обновление данных сотрудника супер-юзером"""
    url = app.url_path_for(
        "update_employee_partially",
        company_pk=create_employee.company_id,
        user_pk=create_employee.user_id,
    )
    response = await superuser_client.patch(
        url,
        json=EmployeeIn(**random_employee.to_json()).model_dump(),
    )
    result = await session.execute(
        select(Employee).where(
            Employee.user_id == random_employee.user_id,
            Employee.telegram == random_employee.telegram,
        ),
    )
    after_update_employee = result.unique().scalar_one_or_none()
    await session.refresh(after_update_employee)
    assert response.status_code == status.HTTP_200_OK
    assert await check_object_data(
        after_update_employee,
        random_employee.to_json(),
    )


@pytest.mark.anyio
async def test_partial_update_employee_by_unauthorized(
    async_client: AsyncClient,
    session: AsyncSession,
    create_employee: Employee,
    random_employee: Employee,
):
    """Тест проверяет частичное обновление данных сотрудника не авторизированным пользователем"""
    url = app.url_path_for(
        "update_employee_partially",
        company_pk=create_employee.company_id,
        user_pk=create_employee.user_id,
    )
    response = await async_client.patch(
        url,
        json=EmployeeOptional(**random_employee.to_json()).model_dump(),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    result = await session.execute(
        select(Employee).where(
            Employee.user_id == create_employee.user_id,
            Employee.telegram == create_employee.telegram,
        ),
    )
    after_update_employee = result.unique().scalar_one_or_none()
    await session.refresh(after_update_employee)
    assert await check_object_data(
        after_update_employee,
        create_employee.to_json(),
    )


@pytest.mark.anyio
async def test_add_new_employee_by_superuser(
    superuser_client: AsyncClient,
    init_another_employee_data: dict,
    session: AsyncSession,
):
    """Тест на добавление нового пользователя в компанию от лица супер-юзера"""
    url = app.url_path_for("add_employee")
    company_stmt = await session.execute(
        select(Company)
        .where(Company.id == init_another_employee_data["company_id"])
        .options(selectinload(Company.employees)),
    )
    company = company_stmt.scalar_one_or_none()
    await session.refresh(company)
    employees_count_before = len(company.employees)
    response = await superuser_client.post(url, json=init_another_employee_data)
    await session.refresh(company)
    employees_count_after = len(company.employees)
    assert response.status_code == status.HTTP_201_CREATED
    assert employees_count_before == employees_count_after - 1
