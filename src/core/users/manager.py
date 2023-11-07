from typing import Optional
from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin, models
from starlette.responses import Response
from src.core.users.models import User
from src.core.config import get_settings
from src.core.users.schemas import UserUpdate
from datetime import datetime


settings = get_settings()


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_login(
        self,
        user: models.UP,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        update_json = await user.to_json()
        update_json["last_login"] = datetime.now()

        await self.update(UserUpdate(**update_json), user, safe=True, request=request)
