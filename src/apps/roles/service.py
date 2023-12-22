from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
from src.core.interfaces import IService

if TYPE_CHECKING:
    from src.core.users.models import Role
    from src.apps.roles.repository import RoleRepository


class RoleService(IService):
    def __init__(self, repo: RoleRepository):
        self._repo = repo

    async def get(self) -> Sequence[Role]:
        return await self._repo.get()

    async def get_by_name(self, name: str) -> Role:
        return await self._repo.get_by_name(name=name)

    async def update(self, old_name: str, new_name: str, partial: bool = False) -> Role:
        return await self._repo.update(
            old_name=old_name,
            new_name=new_name,
            partial=partial,
        )

    async def delete_role(self, name: str) -> bool:
        return await self._repo.delete_role(name=name)

    async def delete(self) -> None:
        return await self._repo.delete()

    async def create(self, in_model) -> Role:
        return await self._repo.create(in_model=in_model)
