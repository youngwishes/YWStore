from __future__ import annotations
from typing import TYPE_CHECKING

from fastapi_users.exceptions import UserAlreadyExists
from fastapi import status

from src.apps.users.models import User
from src.apps.users.schemas import UserUpdate, UserIn
from src.core.exceptions import UniqueConstraintError

if TYPE_CHECKING:
    from src.apps.users.service import UserService


class UserController:
    def __init__(self, service: UserService):
        self._service = service

    async def get_user_by_pk(self, user_pk: int) -> User:
        return await self._service.get_user_or_404(user_pk=user_pk)

    async def update(self, user_pk: int, data: UserUpdate) -> User:
        user = await self._service.get_user_or_404(user_pk=user_pk)
        try:
            return await self._service.update(user_update=data, user=user, safe=True)
        except UserAlreadyExists:
            raise UniqueConstraintError(
                detail="Пользователь с почтой <%s>  уже зарегистрирован в системе."
                % data.email,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def delete(self, user_pk: int) -> None:
        user = await self._service.get_user_or_404(user_pk=user_pk)
        await self._service.delete(user=user)

    async def create(self, user_data: UserIn) -> User:
        try:
            return await self._service.create(user_create=user_data, safe=True)
        except UserAlreadyExists:
            raise UniqueConstraintError(
                detail="Пользователь с почтой <%s>  уже зарегистрирован в системе."
                % user_data.email,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
