from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
from src.core.interfaces import IRepository
from src.core.users.models import Role
from sqlalchemy.sql import delete, select, update

if TYPE_CHECKING:
    from src.apps.roles.schemas import RoleIn
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.core.users.models import User


class RoleRepository(IRepository):
    model: Role = Role

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self) -> Sequence[Role]:
        roles = await self._session.execute(select(self.model))
        return roles.unique().scalars().all()

    async def get_by_pk(self, role_pk: int) -> Role | None:
        role = await self._session.execute(
            select(self.model).where(self.model.id == role_pk),
        )
        return role.unique().scalar_one_or_none()

    async def get_by_name(self, name: str) -> Role | None:
        role = await self._session.execute(
            select(self.model).where(self.model.name == name),
        )
        return role.unique().scalar_one_or_none()

    async def delete(self) -> None:
        await self._session.execute(delete(self.model))
        await self._session.commit()

    async def delete_role(self, role_pk: int) -> None:
        await self._session.execute(
            delete(self.model).where(self.model.id == role_pk),
        )
        await self._session.commit()

    async def update(
        self,
        role_pk: int,
        new_name: str,
        partial: bool = False,
    ) -> Role | None:
        updated_role = await self._session.execute(
            update(self.model)
            .returning(self.model)
            .where(self.model.id == role_pk)
            .values(name=new_name),
        )
        await self._session.commit()
        return updated_role.unique().scalar_one_or_none()

    async def create(self, in_model: RoleIn) -> Role:
        instance = self.model(**in_model.model_dump())  # type: ignore[call-arg]
        self._session.add(instance)
        await self._session.commit()
        await self._session.refresh(instance)
        return instance

    async def add_roles_to_user(self, user: User, roles_set: set[str]) -> User:
        roles_stmt = await self._session.execute(
            select(self.model).where(
                self.model.name.in_(roles_set.difference(user.roles_set)),
            ),
        )
        user.roles.extend(roles_stmt.unique().scalars().all())
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
