from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import Depends

from src.apps.roles.controller import RoleController
from src.core.users.depends import get_session, get_user_service
from src.apps.roles.repository import RoleRepository
from src.apps.roles.service import RoleService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.core.users.manager import UserService


async def _user_role_repository(
    session: AsyncSession = Depends(get_session),
) -> RoleRepository:
    yield RoleRepository(session=session)


async def _user_role_service(
    repository: RoleRepository = Depends(_user_role_repository),
) -> RoleService:
    yield RoleService(repo=repository)


async def get_role_controller(
    role_service: RoleService = Depends(_user_role_service),
    user_service: UserService = Depends(get_user_service),
) -> RoleController:
    yield RoleController(role_service=role_service, user_service=user_service)


__all__ = ["get_role_controller"]
