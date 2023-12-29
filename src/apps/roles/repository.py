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
    model = Role

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self) -> Sequence[Role]:
        roles = await self.session.execute(select(self.model))
        return roles.unique().scalars().all()

    async def get_by_name(self, name: str) -> Role:
        role = await self.session.execute(
            select(self.model).where(self.model.name == name),
        )
        return role.unique().scalar_one_or_none()

    async def delete(self) -> None:
        await self.session.execute(delete(self.model))
        await self.session.commit()

    async def delete_role(self, name: str) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.name == name),
        )
        await self.session.commit()
        return bool(result.rowcount)

    async def update(self, old_name: str, new_name: str, partial: bool = False) -> Role:
        updated_role = await self.session.execute(
            update(self.model)
            .returning(self.model)
            .where(self.model.name == old_name)
            .values(name=new_name),
        )
        await self.session.commit()
        return updated_role.unique().scalar_one_or_none()

    async def create(self, in_model: RoleIn) -> Role:
        instance = self.model(**in_model.model_dump())  # type: ignore[call-arg]
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def add_roles_to_user(self, user: User, roles_set: set[str]) -> User:
        user_roles_name_set = {role.name for role in user.roles}
        roles_stmt = await self.session.execute(
            select(self.model).where(
                self.model.name.in_(roles_set.difference(user_roles_name_set)),
            ),
        )
        user.roles.extend(roles_stmt.unique().scalars().all())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
