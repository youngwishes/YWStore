from __future__ import annotations
import functools
from typing import Sequence, Callable, Any, TYPE_CHECKING
from fastapi import Depends
from src.core.users.models import User
from src.permissions.service import PermissionService
from src.core.users.depends import get_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_from_kwargs(kwargs: dict) -> User | None:
    for key, value in kwargs.items():
        if isinstance(value, User):
            return value


async def get_object_pk(kwargs: dict) -> int | None:
    for key, value in kwargs.items():
        if key.startswith("pk") or key.endswith("pk") or key.endswith("id"):
            return value


def permissions(
    allowed_roles: Sequence[str],
    validators: Sequence[Callable] = None,
    session: AsyncSession = Depends(get_session),
) -> Any:
    def permission_service(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            user = await get_user_from_kwargs(kwargs)
            object_pk = await get_object_pk(kwargs)
            service = PermissionService(
                user=user,
                session=session,
                allowed_roles=allowed_roles,
                validators=validators,
                object_pk=object_pk,
            )
            await service.execute()
            result = await func(*args, **kwargs)
            return result

        return wrapped

    return permission_service
