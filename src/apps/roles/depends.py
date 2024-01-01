from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import Depends

from src.apps.roles.controller import RoleController
from src.core.users.depends import get_session, get_user_manager
from src.apps.roles.repository import RoleRepository
from src.apps.roles.service import RoleService
from src.core.users.manager import UserManager

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def _user_role_repository(
    session: AsyncSession = Depends(get_session),
) -> RoleRepository:
    yield RoleRepository(session=session)


async def _user_role_service(
    repository: RoleRepository = Depends(_user_role_repository),
) -> RoleService:
    yield RoleService(repo=repository)


async def user_role_controller(
    role_service: RoleService = Depends(_user_role_service),
    user_manager: UserManager = Depends(get_user_manager),
):
    yield RoleController(role_service=role_service, user_manager=user_manager)


__all__ = ["user_role_controller"]
