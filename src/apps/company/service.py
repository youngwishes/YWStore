from __future__ import annotations
from fastapi import status
from src.core.exceptions import UniqueConstraintError, NotFoundError
from src.core.interfaces import IService
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from src.apps.company.schemas import CompanyIn, CompanyOptional
    from src.apps.company.repository import CompanyRepository
    from src.apps.company.models import Company


class CompanyService(IService):
    def __init__(self, repo: CompanyRepository) -> None:
        self._repo = repo

    async def get(self) -> Sequence[Company]:
        return await self._repo.get()

    async def create(self, in_model: CompanyIn) -> Company:
        if await self.get_by_name(name=in_model.name):
            raise UniqueConstraintError(
                detail="Компания с названием <%s> уже зарегистрирована в системе"
                % in_model.name,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return await self._repo.create(in_model=in_model)

    async def get_company_or_404(self, company_pk: int) -> Company | None:
        if company := await self._repo.get_by_pk(company_pk=company_pk):
            return company
        raise NotFoundError(
            detail="Компания с идентификатором %s не была найдена" % company_pk,
            status_code=404,
        )

    async def get_by_name(self, name: str) -> Company | None:
        return await self._repo.get_by_name(name=name)

    async def delete(self) -> None:
        await self._repo.delete()

    async def delete_by_pk(self, company_pk: int) -> None:
        if not await self._repo.delete_by_pk(company_pk=company_pk):
            raise NotFoundError(
                detail="Компания с идентификатором %s не была найдена" % company_pk,
                status_code=404,
            )

    async def update_is_verified(self, company_pk: int, is_verified: bool) -> Company:
        await self.get_company_or_404(company_pk=company_pk)
        return await self._repo.update_is_verified(
            pk=company_pk,
            is_verified=is_verified,
        )

    async def update_is_hidden(self, company_pk: int, is_hidden: bool) -> Company:
        await self.get_company_or_404(company_pk=company_pk)
        return await self._repo.update_is_hidden(
            company_pk=company_pk,
            is_hidden=is_hidden,
        )

    async def update(
        self,
        company_pk: int,
        data: CompanyIn | CompanyOptional,
        partial: bool,
    ) -> Company:
        await self.get_company_or_404(company_pk=company_pk)
        if await self.get_by_name(name=data.name):
            raise UniqueConstraintError(
                detail="Компания с названием <%s> уже зарегистрирована в системе"
                % data.name,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return await self._repo.update(
            company_pk=company_pk,
            data=data,
            partial=partial,
        )
