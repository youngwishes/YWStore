from __future__ import annotations

import functools

from fastapi import Depends
from fastapi import status

from src.apps.employee.schemas import EmployeeIn
from src.apps.roles.exceptions import AdminRequiredError
from src.apps.users.models import User
from src.core.auth.strategy import get_current_user
from src.apps.roles.enums import CompanyRoles
from src.core.exceptions import IsOwnerError


def allow_superuser(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, User) and v.is_superuser:
                return v
        return await func(*args, **kwargs)

    return wrapped


@allow_superuser
async def get_company_admin(
    company_pk: int,
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.employee or current_user.employee.company_id != company_pk:
        raise IsOwnerError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не имеете доступа к данной компании.",
        )
    if CompanyRoles.ADMIN in current_user.roles_set:
        return current_user
    raise AdminRequiredError(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Необходимо обладать правами администратора.",
    )


@allow_superuser
async def get_company_admin_post_query(
    employee: EmployeeIn,
    current_user: User = Depends(get_current_user),
) -> User:
    if (
        not current_user.employee
        or current_user.employee.company_id != employee.company_id
    ):
        raise IsOwnerError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не имеете доступа к данной компании.",
        )
    if CompanyRoles.ADMIN in current_user.roles_set:
        return current_user
    raise AdminRequiredError(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Необходимо обладать правами администратора.",
    )


@allow_superuser
async def get_current_employee(
    user_pk: int,
    company_pk: int,
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.id != user_pk:
        raise IsOwnerError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )
    if current_user.employee.company_id != company_pk:
        raise IsOwnerError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не имеете доступа к данной компании.",
        )
    return current_user
