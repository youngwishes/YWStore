import pytest
from src.apps.company.enums import CompanyType


@pytest.fixture
def company_init_data():
    return {
        "name": "Test",
        "director_fullname": "Test",
        "type": CompanyType.LLC,
        "jur_address": {"Country": "Russian Federation"},
        "fact_address": {"Country": "Russian Federation"},
    }
