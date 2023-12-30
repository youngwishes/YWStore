from __future__ import annotations
from typing import Sequence, Callable, TYPE_CHECKING
from fastapi import status
from src.apps.roles.exceptions import RoleNotExists

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.core.users.models import User


class PermissionChecker:
    def __init__(
        self,
        *,
        user: User,
        session: AsyncSession,
        allowed_roles: Sequence[str],
        validators: Sequence[Callable] = None,
        object_pk: int = None,
        **kwargs,
    ) -> None:
        self.allowed_roles = allowed_roles
        self.session = session
        self.validators = validators
        self.object_pk = object_pk
        self.user = user
        self.kwargs = kwargs

    @property
    def user_roles_set(self) -> set[str]:
        return {role.name for role in self.user.roles}

    def _check_user_roles(self) -> None:
        """Проверка, что у пользователя принадлежит хотя бы одной из ролей в allowed_roles"""
        if self.user and not self.user.is_superuser:
            if not self.user_roles_set.intersection(self.allowed_roles):
                raise RoleNotExists(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Пользователь не является никем из: {self.allowed_roles}",
                )

    async def _run_validators(self) -> None:
        """Запуск валидаторов"""
        for validator in self.validators:
            await validator(
                user=self.user,
                object_pk=self.object_pk,
                session=self.session,
                **self.kwargs,
            )

    async def execute(self) -> None:
        """Запуск сервиса, точка входа."""
        self._check_user_roles()
        await self._run_validators()
