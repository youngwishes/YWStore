from typing import Sequence
from src.apps.company.service import CompanyService
from src.apps.company.models import Company
from src.apps.company.schemas import CompanyIn, CompanyOptional


class CompanyController:
    def __init__(self, company_service: CompanyService) -> None:
        self._service = company_service

    async def create(self, in_model: CompanyIn) -> Company:
        return await self._service.create(in_model=in_model)

    async def update(
        self,
        company_pk: int,
        data: CompanyIn | CompanyOptional,
        partial: bool,
    ) -> Company:
        return await self._service.update(
            company_pk=company_pk,
            data=data,
            partial=partial,
        )

    async def get(self) -> Sequence[Company]:
        return await self._service.get()

    async def get_company_or_404(self, company_pk: int) -> Company:
        return await self._service.get_company_or_404(company_pk=company_pk)

    async def delete(self) -> None:
        await self._service.delete()

    async def delete_by_pk(self, company_pk: int) -> None:
        await self._service.delete_by_pk(company_pk=company_pk)

    async def update_is_hidden(self, company_pk: int, is_hidden: bool) -> Company:
        return await self._service.update_is_hidden(
            company_pk=company_pk,
            is_hidden=is_hidden,
        )

    async def update_is_verified(self, company_pk: int, is_verified: bool) -> Company:
        return await self._service.update_is_verified(
            company_pk=company_pk,
            is_verified=is_verified,
        )
