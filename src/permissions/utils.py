from __future__ import annotations
import functools
from typing import Sequence, Callable, TYPE_CHECKING, Any
from fastapi import Depends
from src.core.users.models import User
from src.permissions.service import PermissionChecker
from src.core.users.depends import get_session
from src.core.utils import import_schema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def is_member(user: User, role: str) -> bool:
    return role in [role.name for role in user.roles]


def allow_superuser(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        for key, value in kwargs.items():
            if isinstance(value, User):
                if value.is_superuser:
                    return
        return await func(*args, **kwargs)

    return wrapped


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
    def permission_service(func) -> Callable:
        for key, value in func.__annotations__.items():
            if class_schema := import_schema(value):
                func.__annotations__[key] = class_schema

        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            user = await get_user_from_kwargs(kwargs)
            object_pk = await get_object_pk(kwargs)
            checker = PermissionChecker(
                user=user,
                session=session,
                allowed_roles=allowed_roles,
                validators=validators,
                object_pk=object_pk,
            )
            await checker.execute()
            result = await func(*args, **kwargs)
            return result

        return wrapped

    return permission_service
