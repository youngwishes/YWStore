from typing import Optional
from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from src.core.users.models import User
from src.core.config import get_settings

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
