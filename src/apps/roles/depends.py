from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import Depends
from src.core.users.depends import get_session
from src.apps.roles.repository import RoleRepository
from src.apps.roles.service import RoleService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def _user_role_repository(
    session: AsyncSession = Depends(get_session),
) -> RoleRepository:
    yield RoleRepository(session=session)


async def user_role_service(
    repository: RoleRepository = Depends(_user_role_repository),
) -> RoleService:
    yield RoleService(repo=repository)
