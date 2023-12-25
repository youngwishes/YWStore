from typing import Sequence, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.users.models import User


class PermissionService:
    def __init__(
        self,
        user: User,
        session: AsyncSession,
        allowed_roles: Sequence[str],
        validators: Sequence[Callable] = None,
    ) -> None:
        self.allowed_roles = allowed_roles
        self._session = session
        self.validators = validators
        self.user = user

    @property
    def user(self) -> User:
        return self._user

    @user.setter
    def user(self, user: User) -> None:
        print(user.roles)
        self._user = user
