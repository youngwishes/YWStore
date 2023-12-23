from typing import Sequence, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.core.users.auth import current_user
from src.core.users.models import User
from src.permissions.service import PermissionService
from src.core.users.depends import get_session


def permission_service(allowed_roles: Sequence[str]) -> Callable:
    async def wrapped(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
    ) -> PermissionService:
        yield PermissionService(user=user, session=session, allowed_roles=allowed_roles)

    return wrapped
