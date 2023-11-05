from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, List
from src.core.users.schemas import UserOut
from src.core.users.models import User
from fastapi import Depends
from src.core.sql.database import get_db
from sqlalchemy.sql import select

from fastapi import APIRouter

router = APIRouter()

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@router.get("/users", response_model=List[UserOut])
async def all_users(db: AsyncSession = Depends(get_db)) -> Sequence[User]:
    users = await db.execute(select(User))
    return users.scalars().all()
