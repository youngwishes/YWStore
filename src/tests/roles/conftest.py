from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from src.core.users.models import Role

from src.tests.defaults import TEST_ROLE_NAME

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def init_role_data() -> dict:
    return {"name": TEST_ROLE_NAME}


@pytest.fixture
async def create_role(init_role_data: dict, session: AsyncSession) -> Role:
    instance = Role(**init_role_data)  # type: ignore[call-arg]
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance
