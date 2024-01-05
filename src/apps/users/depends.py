from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.controller import UserController
from src.apps.users.models import User
from src.core.sql.database import get_session
from src.apps.users.service import UserService


async def _get_user_db(
    session: AsyncSession = Depends(get_session),
) -> SQLAlchemyUserDatabase:
    yield SQLAlchemyUserDatabase(session, User)


async def _get_user_service(user_db=Depends(_get_user_db)) -> UserService:
    yield UserService(user_db)


async def get_user_controller(
    service: UserService = Depends(_get_user_service),
) -> UserController:
    yield UserController(service=service)


__all__ = ["get_user_controller"]
