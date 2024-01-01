from __future__ import annotations
from typing import TYPE_CHECKING, Sequence

from src.apps.roles.enums import CompanyRoles
from src.core.exceptions import UniqueConstraintError, NotFoundError
from src.core.interfaces import IService
from fastapi import status

if TYPE_CHECKING:
    from src.core.users.models import Role, User
    from src.apps.roles.repository import RoleRepository
    from src.apps.roles.schemas import RoleIn


class RoleService(IService):
    def __init__(self, repo: RoleRepository) -> None:
        self._repo = repo

    async def create(self, in_model: RoleIn) -> Role:
        await self._check_role_already_exist(name=in_model.name)
        return await self._repo.create(in_model=in_model)

    async def delete_role(self, role_pk: int) -> None:
        await self.get_role_or_404(role_pk=role_pk)
        await self._repo.delete_role(role_pk=role_pk)

    async def get(self) -> Sequence[Role]:
        return await self._repo.get()

    async def update(self, role_pk: int, new_name: str, partial: bool = False) -> Role:
        await self.get_role_or_404(role_pk=role_pk)
        return await self._repo.update(
            role_pk=role_pk,
            new_name=new_name,
            partial=partial,
        )

    async def delete(self) -> None:
        return await self._repo.delete()

    async def add_roles_to_user(
        self,
        user: User,
        roles_list: Sequence[CompanyRoles],
    ) -> User:
        return await self._repo.add_roles_to_user(user=user, roles_set=set(roles_list))

    async def get_role_or_404(self, role_pk: int) -> Role:
        if role := await self._repo.get_by_pk(role_pk=role_pk):
            return role
        raise NotFoundError(
            detail="Роль с идентификатором %s не была найдена в системе" % role_pk,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    async def _check_role_already_exist(self, name: str):
        if await self._repo.get_by_name(name=name):
            raise UniqueConstraintError(
                detail="Роль с названием %s уже существует в системе" % name,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
