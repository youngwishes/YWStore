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
    sorted_users = [[], []]
    for test_user in create_test_users:
        employee = {
            "company_id": create_test_company.id,
            "user_id": test_user.id,
            "vk": "string",
            "telegram": "string",
            "extra_data": "string",
            "is_active": test_user.is_active,
            "phone_number": "string",
        }
        if test_user.is_active:
            sorted_users[1].append(employee)
            continue
        sorted_users[0].append(employee)
    return sorted_users
