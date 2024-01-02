from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.users.models import User
from src.core.sql.database import get_session
from src.core.users.manager import UserService


async def get_user_db(
    session: AsyncSession = Depends(get_session),
) -> SQLAlchemyUserDatabase:
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_service(user_db=Depends(get_user_db)) -> UserService:
    yield UserService(user_db)
