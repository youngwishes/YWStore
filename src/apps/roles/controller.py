from __future__ import annotations
from typing import TYPE_CHECKING, Sequence

from src.apps.roles.enums import CompanyRoles
from src.apps.roles.schemas import RoleIn
from src.apps.users.models import Role, User

if TYPE_CHECKING:
    from src.apps.roles.service import RoleService
    from src.apps.users.service import UserService


class RoleController:
    def __init__(
        self,
        role_service: RoleService,
        user_service: UserService,
    ):
        self._role_service = role_service
        self._user_service = user_service

    async def get(self) -> Sequence[Role]:
        return await self._role_service.get()

    async def update(self, role_pk: int, new_name: str, partial: bool = False) -> Role:
        return await self._role_service.update(
            role_pk=role_pk,
            new_name=new_name,
            partial=partial,
        )

    async def delete_role(self, role_pk: int) -> None:
        await self._role_service.delete_role(role_pk=role_pk)

    async def delete(self) -> None:
        return await self._role_service.delete()

    async def create(self, in_model: RoleIn) -> Role:
        return await self._role_service.create(in_model=in_model)

    async def add_roles_to_user(
        self,
        user_pk: int,
        roles_list: Sequence[CompanyRoles],
    ) -> User:
        user = await self._user_service.get_user_or_404(user_pk=user_pk)
        return await self._role_service.add_roles_to_user(
            user=user,
            roles_list=roles_list,
        )
