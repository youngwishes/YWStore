from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import status
from src.apps.roles.enums import CompanyRoles
from src.apps.roles.exceptions import AdminRequiredError
from src.core.exceptions import IsOwnerError
from src.permissions.utils import allow_superuser, is_member

if TYPE_CHECKING:
    from src.core.users.models import User


@allow_superuser
async def is_company_admin(*, user: User, object_pk: int, **kwargs) -> None:
    if not is_member(user, CompanyRoles.ADMIN):
        raise AdminRequiredError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Необходимо обладать правами администратора.",
        )
    if not user.employee or user.employee.company_id != object_pk:
        raise IsOwnerError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не имеете доступа к данной компании.",
        )
