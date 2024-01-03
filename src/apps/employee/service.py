from __future__ import annotations

from fastapi import status
from src.core.exceptions import UniqueConstraintError
from src.core.interfaces import IService
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from src.apps.employee.schemas import EmployeeIn, EmployeeOptional
    from src.apps.employee.repository import EmployeeRepository
    from src.apps.employee.models import Employee


class EmployeeService(IService):
    def __init__(self, repo: EmployeeRepository):
        self._repo = repo

    async def get(self, company_pk: int) -> Sequence[Employee]:
        return await self._repo.get(company_pk=company_pk)

    async def create(self, in_model: EmployeeIn) -> Employee:
        await self._check_user_already_in_company(
            company_pk=in_model.company_id,
            user_pk=in_model.user_id,
        )
        return await self._repo.create(in_model=in_model)

    async def update(
        self,
        pk: int,
        company_pk: int,
        data: EmployeeIn | EmployeeOptional,
        partial: bool = False,
    ) -> Employee:
        return await self._repo.update(
            user_pk=pk,
            company_pk=company_pk,
            data=data,
            partial=partial,
        )

    async def delete(self):
        return await self._repo.delete()

    async def delete_from_company_by_pk(self, user_pk: int, company_pk: int):
        return await self._repo.delete_from_company_by_pk(
            user_pk=user_pk,
            company_pk=company_pk,
        )

    async def _check_user_already_in_company(
        self,
        company_pk: int,
        user_pk: int,
    ) -> None:
        if await self._repo._check_user_already_in_company(
            company_pk=company_pk,
            user_pk=user_pk,
        ):
            raise UniqueConstraintError(
                detail="Пользователь уже состоит в компании",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
