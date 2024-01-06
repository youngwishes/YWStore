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
        self._session = session

    async def get(self, company_pk: int) -> Sequence[Employee]:
        employees = await self._session.execute(
            select(self.model)
            .where(self.model.company_id == company_pk, self.model.is_active == true())
            .options(selectinload(self.model.user)),
        )
        return employees.unique().scalars().all()

    async def delete(self):
        await self._session.execute(update(self.model).values(is_active=False))
        await self._session.commit()

    async def delete_from_company_by_pk(self, user_pk: int, company_pk: int):
        await self._session.execute(
            update(self.model)
            .where(self.model.company_id == company_pk, self.model.user_id == user_pk)
            .values(is_active=False),
        )
        await self._session.commit()

    async def check_user_already_in_company(
        self,
        company_pk: int,
        user_pk: int,
    ) -> Employee | None:
        employee = await self._session.execute(
            select(self.model).where(
                self.model.company_id == company_pk,
                self.model.user_id == user_pk,
            ),
        )
        return employee.unique().scalar_one_or_none()

    async def update(
        self,
        user_pk: int,
        company_pk: int,
        data: EmployeeIn | EmployeeOptional,
        partial: bool = False,
    ) -> Employee:
        updated_employee = await self._session.execute(
            update(self.model)
            .returning(self.model)
            .where(self.model.user_id == user_pk, self.model.company_id == company_pk)
            .values(**data.model_dump(exclude_none=partial))
            .options(selectinload(Employee.user)),
        )
        await self._session.commit()
        return updated_employee.unique().scalar_one_or_none()

    async def create(self, in_model: EmployeeIn) -> Employee:
        new_employee = self.model(**in_model.model_dump())  # type: ignore[call-arg]
        self._session.add(new_employee)
        await self._session.commit()
        await self._session.refresh(new_employee)
        return new_employee
