from __future__ import annotations
from src.core.interfaces import IService
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from src.apps.employee.schemas import EmployeeIn
    from src.apps.employee.repository import EmployeeRepository
    from src.apps.employee.models import Employee


class EmployeeService(IService):
    def __init__(self, repo: EmployeeRepository):
        self._repo = repo

    async def get(self, pk: int) -> Sequence[Employee]:
        return await self._repo.get(pk=pk)

    async def create(self, in_model: EmployeeIn) -> Employee:
        return await self._repo.create(in_model=in_model)

    async def update(self, pk, data, partial):
        return await self._repo.update(pk=pk, data=data, partial=partial)

    async def delete(self):
        return await self._repo.delete()

    async def delete_from_company_by_pk(self, pk: int, company_pk: int):
        return await self._repo.delete_from_company_by_pk(pk=pk, company_pk=company_pk)

    async def check_if_exists(self, company_pk: int, user_pk: int):
        return await self._repo.check_if_exists(company_pk=company_pk, user_pk=user_pk)
