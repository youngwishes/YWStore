from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.core.sql.database import Base
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, Integer, DateTime, Boolean, func


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(length=64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(length=64), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(length=64), nullable=True)
    email: Mapped[str] = mapped_column(
        String(length=320),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    async def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
