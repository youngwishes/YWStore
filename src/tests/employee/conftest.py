from __future__ import annotations

import random
from typing import TYPE_CHECKING, Sequence

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.employee.models import Employee
from src.apps.employee.schemas import EmployeeIn

if TYPE_CHECKING:
    from src.apps.users.models import User
    from src.apps.company.models import Company


@pytest.fixture
def init_employee_data(
    create_test_company: Company,
    create_test_user: User,
):
    return {
        "company_id": create_test_company.id,
        "user_id": create_test_user.id,
        "vk": "string",
        "telegram": "string",
        "extra_data": "string",
        "is_active": True,
        "phone_number": "string",
    }


@pytest.fixture
async def create_employee(
    session: AsyncSession,
    init_employee_data: dict,
) -> Employee:
    employee = Employee(**EmployeeIn(**init_employee_data).model_dump())  # type: ignore[call-arg]
    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


@pytest.fixture
async def create_employees_many(
    create_test_users: Sequence[User],
    session: AsyncSession,
    init_employee_data: dict,
) -> Sequence[Employee]:
    employees = []
    for i, user in enumerate(create_test_users):
        init_employee_data["user_id"] = user.id
        init_employee_data["is_active"] = user.is_active
        init_employee_data["vk"] = f"{i}"
        init_employee_data["telegram"] = f"{i}"
        init_employee_data["extra_data"] = f"{i}"
        employee = Employee(**EmployeeIn(**init_employee_data).model_dump())  # type: ignore[call-arg]

        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        employees.append(employee)
    return employees


@pytest.fixture
async def random_employee(
    create_employees_many: Sequence[Employee],
    session: AsyncSession,
):
    result = await session.execute(select(Employee))
    companies = result.unique().scalars().all()
    return companies[random.randint(0, len(companies) - 1)]


@pytest.fixture
def active_employees(create_employees_many: Sequence[Employee]) -> Sequence[Employee]:
    return [
        test_employee
        for test_employee in create_employees_many
        if test_employee.is_active
    ]


@pytest.fixture
def inactive_employees(create_employees_many: Sequence[Employee]) -> Sequence[Employee]:
    return [
        test_employee
        for test_employee in create_employees_many
        if not test_employee.is_active
    ]
