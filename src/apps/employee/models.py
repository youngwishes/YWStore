from __future__ import annotations
from src.core.mixins import JSONRepresentationMixin
from src.core.sql.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String, Boolean
from src.core.users.models import User


class Employee(JSONRepresentationMixin, Base):
    __tablename__ = "employees"

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        primary_key=True,
    )
    telegram: Mapped[str] = mapped_column(
        "Ссылка на телеграм",
        String(length=256),
        nullable=True,
    )
    vk: Mapped[str] = mapped_column("Ссылка на ВК", String(length=256), nullable=True)
    phone_number: Mapped[str] = mapped_column(
        "Номер телефона",
        String(length=32),
        nullable=True,
    )
    extra_data: Mapped[str] = mapped_column(
        "Дополнительная информация о сотруднике",
        String,
        nullable=True,
    )
    user: Mapped[User] = relationship(
        "User",
        backref="employee",
        lazy="joined",
        uselist=False,
    )
    is_active: Mapped[bool] = mapped_column("Профиль активен", Boolean, default=True)

    def __repr__(self) -> str:
        return f"Employee(user={self.user_id}, company={self.company_id})"
