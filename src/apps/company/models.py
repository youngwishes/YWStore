from __future__ import annotations
from src.core.sql.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Float,
    Boolean,
    func,
    SmallInteger,
)
from datetime import datetime
from src.core.mixins import JSONRepresentationMixin
from sqlalchemy.dialects.postgresql import JSONB
from src.apps.employee.models import Employee


class Company(JSONRepresentationMixin, Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        "Название компании",
        String(length=256),
        unique=True,
        index=True,
    )
    director_fullname: Mapped[str] = mapped_column("ФИО директора", String(length=64))
    type: Mapped[int] = mapped_column("Тип компании", SmallInteger)
    jur_address: Mapped[JSONB] = mapped_column(
        "Юридический адрес",
        JSONB,
        nullable=True,
    )
    fact_address: Mapped[JSONB] = mapped_column(
        "Фактический адрес",
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        "Дата регистрации",
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        "Дата обновления",
        DateTime(timezone=True),
        nullable=True,
    )
    rating: Mapped[float] = mapped_column("Рейтинг", Float, nullable=True, index=True)
    is_hidden: Mapped[bool] = mapped_column("Скрыта в системе", Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column("Подтверждена", Boolean, default=False)
    employees: Mapped[list[Employee]] = relationship("Employee", backref="company")

    def __repr__(self):
        return self.name
