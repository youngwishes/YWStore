from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
import pytest

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
def init_employees_data(
    create_test_company: Company,
    create_test_users: Sequence[User],
):
    return [
        {
            "company_id": create_test_company.id,
            "user_id": test_user.id,
            "vk": "string",
            "telegram": "string",
            "extra_data": "string",
            "is_active": test_user.is_active,
            "phone_number": "string",
        }
        for test_user in create_test_users
    ]


@pytest.fixture
def init_active_employees_data(init_employees_data: Sequence[dict]):
    return [test_user for test_user in init_employees_data if test_user["is_active"]]


@pytest.fixture
def init_inactive_employees_data(init_employees_data: Sequence[dict]):
    return [
        test_user for test_user in init_employees_data if not test_user["is_active"]
    ]
