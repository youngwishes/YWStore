from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.employee.models import Employee
from src.apps.employee.schemas import EmployeeIn

if TYPE_CHECKING:
    from src.core.users.models import User
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
):
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
):
    employees = []
    for user in create_test_users:
        init_employee_data["user_id"] = user.id
        init_employee_data["is_active"] = user.is_active
        employee = Employee(**EmployeeIn(**init_employee_data).model_dump())  # type: ignore[call-arg]

        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        employees.append(employee)
    return employees


@pytest.fixture
def active_employees(create_employees_many: Sequence[Employee]):
    return [
        test_employee
        for test_employee in create_employees_many
        if test_employee.is_active
    ]


@pytest.fixture
def inactive_employees(create_employees_many: Sequence[Employee]):
    return [
        test_employee
        for test_employee in create_employees_many
        if not test_employee.is_active
    ]
