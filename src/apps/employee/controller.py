from __future__ import annotations
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from src.apps.employee.service import EmployeeService
    from src.apps.company.service import CompanyService
    from src.core.users.manager import UserService
    from src.apps.employee.schemas import EmployeeIn, EmployeeOptional
    from src.apps.employee.models import Employee


class EmployeeController:
    def __init__(
        self,
        employee_service: EmployeeService,
        company_service: CompanyService,
        user_service: UserService,
    ) -> None:
        self._employee_service = employee_service
        self._company_service = company_service
        self._user_service = user_service

    async def create(self, in_model: EmployeeIn) -> Employee:
        await self._company_service.get_company_or_404(company_pk=in_model.company_id)
        await self._user_service.get_user_or_404(user_pk=in_model.user_id)
        return await self._employee_service.create(in_model=in_model)

    async def get(self, company_pk: int) -> Sequence[Employee]:
        await self._company_service.get_company_or_404(company_pk=company_pk)
        return await self._employee_service.get(company_pk=company_pk)

    async def delete_from_company_by_pk(self, company_pk: int, user_pk: int) -> None:
        await self._company_service.get_company_or_404(company_pk=company_pk)
        await self._user_service.get_user_or_404(user_pk=user_pk)
        await self._employee_service.delete_from_company_by_pk(
            company_pk=company_pk,
            user_pk=user_pk,
        )

    async def update(
        self,
        company_pk: int,
        user_pk: int,
        data: EmployeeIn | EmployeeOptional,
        partial: bool,
    ) -> Employee:
        await self._company_service.get_company_or_404(company_pk=company_pk)
        await self._user_service.get_user_or_404(user_pk=user_pk)
        return await self._employee_service.update(
            user_pk=user_pk,
            company_pk=company_pk,
            data=data,
            partial=partial,
        )
