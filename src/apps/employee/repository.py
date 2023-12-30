from __future__ import annotations
from typing import Sequence, TYPE_CHECKING

from sqlalchemy import update, true
from sqlalchemy.orm import selectinload
from src.core.interfaces import IRepository
from src.apps.employee.models import Employee
from sqlalchemy.sql import select

if TYPE_CHECKING:
    from src.apps.employee.schemas import EmployeeIn, EmployeeOptional
    from sqlalchemy.ext.asyncio import AsyncSession


class EmployeeRepository(IRepository):
    model: Employee = Employee

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, pk: int) -> Sequence[Employee]:
        employees = await self.session.execute(
            select(self.model)
            .where(self.model.company_id == pk, self.model.is_active == true())
            .options(selectinload(self.model.user)),
        )
        return employees.unique().scalars().all()

    async def delete(self):
        await self.session.execute(update(self.model).values(is_active=False))
        await self.session.commit()

    async def delete_from_company_by_pk(self, pk: int, company_pk: int):
        await self.session.execute(
            update(self.model)
            .where(self.model.company_id == company_pk and self.model.user_id == pk)
            .values(is_active=False),
        )
        await self.session.commit()

    async def check_if_exists(self, company_pk: int, user_pk: int) -> Employee | None:
        employee = await self.session.execute(
            select(self.model).where(
                self.model.company_id == company_pk,
                self.model.user_id == user_pk,
            ),
        )
        return employee.unique().scalar_one_or_none()

    async def update(
        self,
        pk: int,
        company_pk: int,
        data: EmployeeIn | EmployeeOptional,
    ) -> Employee:
        updated_employee = await self.session.execute(
            update(self.model)
            .returning(self.model)
            .where(self.model.user_id == pk, self.model.company_id == company_pk)
            .values(
                **data.model_dump(exclude_none=True),
            ),
        )
        await self.session.commit()
        return updated_employee.unique().scalar_one_or_none()

    async def create(self, in_model: EmployeeIn) -> Employee:
        new_employee = self.model(**in_model.model_dump())  # type: ignore[call-arg]
        self.session.add(new_employee)
        await self.session.commit()
        await self.session.refresh(new_employee)
        return new_employee
