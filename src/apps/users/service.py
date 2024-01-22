from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.exceptions import UserNotExists
from fastapi import status

from src.core.config import get_settings
from src.core.exceptions import NotFoundError
from src.apps.users.models import User
from src.apps.users.schemas import UserUpdate

if TYPE_CHECKING:
    from fastapi import Request
    from starlette.responses import Response
    from fastapi_users.models import UP


settings = get_settings()


class UserService(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_login(
        self,
        user: UP,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        update_json = user.to_json()
        update_json["last_login"] = datetime.now()

        await self.update(UserUpdate(**update_json), user, safe=True, request=request)

    async def get_user_or_404(self, user_pk: int):
        try:
            return await self.get(id=user_pk)
        except UserNotExists:
            raise NotFoundError(
                detail="Пользователь с идентификатором %s не был найден в системе"
                % user_pk,
                status_code=status.HTTP_404_NOT_FOUND,
            )
