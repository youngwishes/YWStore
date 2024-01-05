from __future__ import annotations
from fastapi import Depends
from fastapi import status
from src.apps.roles.exceptions import AdminRequiredError
from src.apps.users.models import User
from src.core.auth.strategy import get_current_user
from src.apps.roles.enums import CompanyRoles


async def get_company_admin(current_user: User = Depends(get_current_user)) -> User:
    if CompanyRoles.ADMIN in current_user.roles_set:
        return current_user
    raise AdminRequiredError(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Необходимо обладать правами администратора.",
    )
