from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import Depends
from src.core.users.depends import get_session
from src.apps.employee.repository import EmployeeRepository
from src.apps.employee.service import EmployeeService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def _employee_repository(
    session: AsyncSession = Depends(get_session),
) -> EmployeeService:
    yield EmployeeRepository(session=session)


async def employee_service(
    repository: EmployeeRepository = Depends(_employee_repository),
):
    yield EmployeeService(repo=repository)
