from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from fastapi import status
from sqlalchemy.sql import select, func
from sqlalchemy.orm import selectinload

from src.main import app
from src.apps.employee.models import Employee
from src.apps.company.models import Company

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
        init_employee_data: dict,
):
    """Тест проверяет получение пользователей из компании"""

    url = app.url_path_for("add_employee")
    response = await async_client.post(url, json=init_employee_data)
    assert response.status_code == status.HTTP_201_CREATED

    url = app.url_path_for("get_employees", company_pk=init_employee_data["company_id"])
    response = await async_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user"]["id"] == init_employee_data["user_id"]
    assert response.json()[0]["user"]["is_active"] is True


@pytest.mark.anyio
async def test_delete_employee_superuser(
        async_client: AsyncClient,
        session: AsyncSession,
        init_employee_data: dict,
        superuser_client: AsyncClient
):
    """Тест проверяет мягкое удаление пользователя из компании от имени супер пользователя"""

    url = app.url_path_for("add_employee")
    response = await async_client.post(url, json=init_employee_data)
    assert response.status_code == status.HTTP_201_CREATED

    employee_request = await session.execute(
        select(Employee)
        .where(Employee.user_id == init_employee_data["user_id"])
    )
    employee_do = employee_request.unique().scalar_one_or_none()
    assert employee_do.is_active is True

    url = app.url_path_for("delete_employee", company_pk=init_employee_data["company_id"],
                           employee_pk=init_employee_data["user_id"])
    response = await superuser_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.refresh(employee_do)
    employee_request = await session.execute(
        select(Employee)
        .where(Employee.user_id == init_employee_data["user_id"])
    )
    employee_after = employee_request.unique().scalar_one_or_none()
    assert employee_after.is_active is False


@pytest.mark.anyio
async def test_delete_employee_authorized(
        async_client: AsyncClient,
        session: AsyncSession,
        init_employee_data: dict,
        authorized_client: AsyncClient
):
    """Тест проверяет мягкое удаление пользователя из компании от имени авторизированного клиента"""

    url = app.url_path_for("add_employee")
    response = await async_client.post(url, json=init_employee_data)
    assert response.status_code == status.HTTP_201_CREATED

    employee_request = await session.execute(
        select(Employee)
        .where(Employee.user_id == init_employee_data["user_id"])
    )
    employee_do = employee_request.unique().scalar_one_or_none()
    assert employee_do.is_active is True

    url = app.url_path_for("delete_employee", company_pk=init_employee_data["company_id"],
                           employee_pk=init_employee_data["user_id"])
    response = await authorized_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await session.refresh(employee_do)
    employee_request = await session.execute(
        select(Employee)
        .where(Employee.user_id == init_employee_data["user_id"])
    )
    employee_after = employee_request.unique().scalar_one_or_none()
    assert employee_after.is_active is True


@pytest.mark.anyio
async def test_delete_employee_unauthorized(
        async_client: AsyncClient,
        session: AsyncSession,
        init_employee_data: dict
):
    """Тест проверяет мягкое удаление пользователя из компании от имени неавторизированного клиента"""

    url = app.url_path_for("add_employee")
    response = await async_client.post(url, json=init_employee_data)
    assert response.status_code == status.HTTP_201_CREATED

    employee_request = await session.execute(
        select(Employee)
        .where(Employee.user_id == init_employee_data["user_id"])
    )
    employee_do = employee_request.unique().scalar_one_or_none()
    assert employee_do.is_active is True

    url = app.url_path_for("delete_employee", company_pk=init_employee_data["company_id"],
                           employee_pk=init_employee_data["user_id"])
    response = await async_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await session.refresh(employee_do)
    employee_request = await session.execute(
        select(Employee)
        .where(Employee.user_id == init_employee_data["user_id"])
    )
    employee_after = employee_request.unique().scalar_one_or_none()
    assert employee_after.is_active is True
