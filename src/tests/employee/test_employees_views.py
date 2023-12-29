from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pytest
from fastapi import status
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select, func

from src.apps.company.models import Company
from src.apps.employee.models import Employee
from src.main import app

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_add_new_employee(
    async_client: AsyncClient,
    init_employee_data: dict,
    session: AsyncSession,
):
    """Тест на добавление нового пользователя в компанию"""
    employees_count = await session.execute(func.count(select(Employee.user_id)))
    assert employees_count.scalar_one() == 0

    employee_stmt = await session.execute(
        select(Employee)
        .where(Employee.user_id == init_employee_data["user_id"])
        .options(selectinload(Employee.user)),
    )
    employee = employee_stmt.scalar_one_or_none()
    assert employee is None

    company_stmt = await session.execute(
        select(Company)
        .where(Company.id == init_employee_data["company_id"])
        .options(selectinload(Company.employees)),
    )
    company = company_stmt.scalar_one_or_none()
    assert len(company.employees) == 0

    url = app.url_path_for("add_employee")
    response = await async_client.post(url, json=init_employee_data)
    assert response.status_code == status.HTTP_201_CREATED

    await session.refresh(company)
    company_stmt = await session.execute(
        select(Company)
        .where(Company.id == init_employee_data["company_id"])
        .options(selectinload(Company.employees)),
    )
    company = company_stmt.scalar_one_or_none()
    assert len(company.employees) == 1

    employees_count = await session.execute(func.count(select(Employee.user_id)))
    assert employees_count.scalar_one() == 1

    employee_stmt = await session.execute(
        select(Employee)
        .where(Employee.user_id == init_employee_data["user_id"])
        .options(selectinload(Employee.company)),
    )
    employee = employee_stmt.unique().scalar_one_or_none()
    assert employee
    assert employee.company


@pytest.mark.anyio
async def test_get_company_employees(
    async_client: AsyncClient,
    session: AsyncSession,
    active_employees,
    create_employees_many: Sequence[Employee],
):
    """Тест проверяет получение пользователей из компании"""
    url = app.url_path_for(
        "get_employees",
        company_pk=active_employees[0].company_id,
    )
    response = await async_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(active_employees)
    assert len(response.json()) != len(create_employees_many)
    for data in response.json():
        assert data["user"]["is_active"] is True


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
        employee_pk=create_employee.user_id,
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
        employee_pk=create_employee.user_id,
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
        employee_pk=create_employee.user_id,
    )
    response = await async_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await session.refresh(employee_do)
    employee_request = await session.execute(
        select(Employee).where(Employee.user_id == create_employee.user_id),
    )
    employee_after = employee_request.unique().scalar_one_or_none()
    assert employee_after.is_active is True
