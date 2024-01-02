from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import Depends
from src.apps.company.depends import get_company_service
from src.core.users.depends import get_session
from src.apps.employee.repository import EmployeeRepository
from src.apps.employee.service import EmployeeService
from src.apps.employee.controller import EmployeeController
from src.core.users.depends import get_user_service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.core.users.manager import UserService
    from src.apps.company.service import CompanyService


async def _employee_repository(
    session: AsyncSession = Depends(get_session),
) -> EmployeeRepository:
    yield EmployeeRepository(session=session)


async def _employee_service(
    repository: EmployeeRepository = Depends(_employee_repository),
) -> EmployeeService:
    yield EmployeeService(repo=repository)


async def get_employee_controller(
    employee_service: EmployeeService = Depends(_employee_service),
    comp_service: CompanyService = Depends(get_company_service),
    user_service: UserService = Depends(get_user_service),
) -> EmployeeController:
    yield EmployeeController(
        employee_service=employee_service,
        company_service=comp_service,
        user_service=user_service,
    )


__all__ = ["get_employee_controller"]
