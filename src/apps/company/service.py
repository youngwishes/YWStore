from __future__ import annotations
from src.core.interfaces import IService
from typing import TYPE_CHECKING, Sequence
from src.apps.company.models import Company

if TYPE_CHECKING:
    from src.apps.company.schemas import CompanyIn, CompanyOptional
    from src.apps.company.repository import CompanyRepository


class CompanyService(IService):
    model = Company

    def __init__(self, repo: CompanyRepository) -> None:
        self._repo = repo

    async def get(self) -> Sequence[Company]:
        return await self._repo.get()

    async def create(self, in_model: CompanyIn) -> Company:
        return await self._repo.create(in_model=in_model)

    async def get_by_pk(self, pk: int) -> Company | None:
        return await self._repo.get_by_pk(pk=pk)

    async def get_by_name(self, name: str) -> Company | None:
        return await self._repo.get_by_name(name=name)

    async def delete(self) -> None:
        await self._repo.delete()

    async def delete_by_pk(self, pk: int) -> bool:
        return await self._repo.delete_by_pk(pk=pk)

    async def update_is_verified(self, pk: int, is_verified: bool) -> Company:
        return await self._repo.update_is_verified(pk=pk, is_verified=is_verified)

    async def update_is_hidden(self, pk: int, is_hidden: bool) -> Company:
        return await self._repo.update_is_hidden(pk=pk, is_hidden=is_hidden)

    async def update(
        self,
        pk: int,
        data: CompanyIn | CompanyOptional,
        partial: bool = False,
    ) -> Company:
        return await self._repo.update(pk=pk, data=data, partial=partial)
