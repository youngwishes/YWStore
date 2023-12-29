from __future__ import annotations
from typing import TYPE_CHECKING
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
