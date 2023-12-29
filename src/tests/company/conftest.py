import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from datetime import datetime
from src.apps.company.enums import CompanyType
from src.apps.company.models import Company
import random


@pytest.fixture
def update_company_data():
    return {
        "name": "Test (Updated)",
        "director_fullname": "Test (Updated)",
        "type": CompanyType.INDIVIDUAL,
        "jur_address": {"Country": "Russian Federation (Updated)"},
        "fact_address": {"Country": "Russian Federation (Updated)"},
    }


@pytest.fixture
def update_partial_company_data():
    return {
        "name": "Test (Updated)",
        "type": CompanyType.INDIVIDUAL,
        "fact_address": {"Country": "Russian Federation (Updated)"},
    }


@pytest.fixture
async def create_test_company_many(session: AsyncSession) -> int:
    to_response_companies = 0
    for i in range(100):
        data = {
            "name": f"Test {i}",
            "director_fullname": f"Test {i}",
            "type": CompanyType.LLC,
            "jur_address": {"Country": "Russian Federation"},
            "fact_address": {"Country": "Russian Federation"},
            "is_verified": random.randint(0, 1),
            "is_hidden": random.randint(0, 1),
            "updated_at": datetime.now(),
        }
        company = Company(**data)  # type: ignore[call-arg]
        if data["is_verified"] and not data["is_hidden"]:
            to_response_companies += 1
        session.add(company)
    await session.commit()
    return to_response_companies


@pytest.fixture
async def random_company(create_test_company_many: int, session: AsyncSession):
    result = await session.execute(
        select(Company).where(
            Company.is_hidden.is_(False),
            Company.is_verified.is_(True),
        ),
    )
    companies = result.unique().scalars().all()
    return companies[random.randint(0, len(companies) - 1)]
