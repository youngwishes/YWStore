from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import Depends
from src.apps.company.depends import company_service
from src.core.users.depends import get_session
from src.apps.employee.repository import EmployeeRepository
from src.apps.employee.service import EmployeeService
from src.apps.employee.controller import EmployeeController
from src.core.users.depends import get_user_manager

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.core.users.manager import UserManager
    from src.apps.company.service import CompanyService


async def _employee_repository(
    session: AsyncSession = Depends(get_session),
) -> EmployeeService:
    yield EmployeeRepository(session=session)


async def _employee_service(
    repository: EmployeeRepository = Depends(_employee_repository),
):
    yield EmployeeService(repo=repository)


async def employee_controller(
    employee_service: EmployeeService = Depends(_employee_service),
    comp_service: CompanyService = Depends(company_service),
    user_manager: UserManager = Depends(get_user_manager),
):
    yield EmployeeController(
        employee_service=employee_service,
        company_service=comp_service,
        user_manager=user_manager,
    )


__all__ = ["employee_controller"]
