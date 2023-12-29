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
async def create_employees_many(
    create_test_users: Sequence[User],
    create_test_company: Company,
    session: AsyncSession,
):
    employees = []
    for user in create_test_users:
        user_data = {
            "company_id": create_test_company.id,
            "user_id": user.id,
            "vk": "string",
            "telegram": "string",
            "extra_data": "string",
            "is_active": user.is_active,
            "phone_number": "string",
        }
        employee = Employee(**EmployeeIn(**user_data).model_dump())  # type: ignore[call-arg]

        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        employees.append(employee)
    return employees


@pytest.fixture
def init_active_employees_data(create_employees_many: Sequence[Employee]):
    return [test_user for test_user in create_employees_many if test_user.is_active]


@pytest.fixture
def init_inactive_employees_data(create_employees_many: Sequence[Employee]):
    return [test_user for test_user in create_employees_many if not test_user.is_active]
