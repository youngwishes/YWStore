from __future__ import annotations
from typing import Sequence, TYPE_CHECKING
from src.core.interfaces import IRepository
from src.apps.company.models import Company
from sqlalchemy.sql import select, delete, update
from datetime import datetime
from sqlalchemy.sql.expression import false, true


if TYPE_CHECKING:
    from src.apps.company.schemas import CompanyIn, CompanyOptional
    from sqlalchemy.ext.asyncio import AsyncSession


class CompanyRepository(IRepository):
    model = Company

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self) -> Sequence[Company]:
        results = await self.session.execute(
            select(self.model).where(
                self.model.is_hidden == false(),
                self.model.is_verified == true(),
            ),
        )
        return results.unique().scalars().all()

    async def create(self, in_model: CompanyIn) -> Company:
        company = self.model(
            **in_model.model_dump(),  # type: ignore[call-arg]
            rating=None,  # type: ignore[call-arg]
            updated_at=datetime.now(),  # type: ignore[call-arg]
        )
        self.session.add(company)
        await self.session.commit()
        return company

    async def get_by_pk(self, pk: int) -> Company | None:
        company = await self.session.execute(
            select(self.model).where(
                self.model.id == pk,
                self.model.is_hidden == false(),
                self.model.is_verified == true(),
            ),
        )
        return company.unique().scalar_one_or_none()

    async def get_by_name(self, name: str) -> Company | None:
        company = await self.session.execute(
            select(self.model).where(self.model.name == name),
        )
        return company.unique().scalar_one_or_none()

    async def delete(self) -> None:
        await self.session.execute(delete(self.model))
        await self.session.commit()

    async def delete_by_pk(self, pk: int) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == pk),
        )
        await self.session.commit()
        return bool(result.rowcount)

    async def update(
        self,
        pk: int,
        data: CompanyIn | CompanyOptional,
        partial: bool = False,
    ) -> Company:
        updated_company = await self.session.execute(
            update(self.model)
            .returning(self.model)
            .where(self.model.id == pk)
            .values(
                **data.model_dump(exclude_none=partial),
                updated_at=datetime.now(),
            ),
        )
        await self.session.commit()
        return updated_company.unique().scalar_one_or_none()

    async def update_is_verified(self, pk: int, is_verified: bool) -> Company | None:
        verified_company = await self.session.execute(
            update(self.model)
            .returning(self.model)
            .where(self.model.id == pk)
            .values(is_verified=is_verified),
        )
        await self.session.commit()
        return verified_company.unique().scalar_one_or_none()

    async def update_is_hidden(self, pk: int, is_hidden: bool) -> Company | None:
        hidden_company = await self.session.execute(
            update(self.model)
            .returning(self.model)
            .where(self.model.id == pk)
            .values(is_hidden=is_hidden),
        )
        await self.session.commit()
        return hidden_company.unique().scalar_one_or_none()
