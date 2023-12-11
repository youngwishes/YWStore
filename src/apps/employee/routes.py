from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
from fastapi import APIRouter, status, Depends
from src.apps.employee.models import Employee
from src.apps.employee.schemas import EmployeeIn, EmployeeOut
from src.core.http_response_schemas import (
    NotFound,
    NotAllowed,
    Unauthorized,
    UniqueConstraint,
)
from src.core.exceptions import NotFoundErrorError, UniqueConstraintError
from src.apps.company.depends import company_service
from src.apps.employee.depends import employee_service
from src.core.users.auth import superuser
from src.core.users.depends import get_user_manager
from fastapi_users.exceptions import UserNotExists

from src.core.users.models import User

if TYPE_CHECKING:
    from src.apps.company.service import CompanyService
    from src.core.users.manager import UserManager
    from src.apps.employee.service import EmployeeService

employee_router = APIRouter()


@employee_router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "model": EmployeeIn,
            "description": "Добавить нового сотрудника в компанию",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": UniqueConstraint,
            "description": "Сотрудник уже состоит в компании",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": Unauthorized,
            "description": "Вы не авторизированы в системе",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": NotAllowed,
            "description": "Вы не можете добавлять сотрудников в компанию",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFound,
            "description": "Объект не найден в системе",
        },
    },
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeIn,
)
async def add_employee(
        employee: EmployeeIn,
        comp_service: CompanyService = Depends(company_service),
        emp_service: EmployeeService = Depends(employee_service),
        user_manager: UserManager = Depends(get_user_manager),
) -> EmployeeOut:
    if not await comp_service.get_by_pk(pk=employee.company_id):
        raise NotFoundErrorError(
            detail="Компания с идентификатором %s не была найдена в системе"
                   % employee.company_id,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    try:
        await user_manager.get(id=employee.user_id)
    except UserNotExists:
        raise NotFoundErrorError(
            detail="Пользователь с идентификатором %s не был найден в системе"
                   % employee.user_id,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if await emp_service.check_if_exists(
            company_pk=employee.company_id,
            user_pk=employee.user_id,
    ):
        raise UniqueConstraintError(
            detail="Пользователь уже состоит в компании",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return await emp_service.create(in_model=employee)


@employee_router.get(
    "/{company_id}",
    responses={
        status.HTTP_200_OK: {
            "model": Sequence[EmployeeOut],
            "description": "Получить сотрудников компании",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": Unauthorized,
            "description": "Вы не авторизированы в системе",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": NotAllowed,
            "description": "Вы не можете получиить сотрудников компании",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFound,
            "description": "Компания не найдена в системе",
        },
    },
    status_code=status.HTTP_200_OK,
    response_model=Sequence[EmployeeOut],
)
async def get_employees(
        company_id: int,
        service: EmployeeService = Depends(employee_service),
) -> Sequence[Employee]:
    return await service.get(pk=company_id)


@employee_router.delete(
    "/{company_id}/{pk}",
    description="Удаление сотрудника.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Сотрудник удален."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Сотрудник, состоящий в этой компании не найден."
        }
    },
)
async def delete_employee(
        pk: int,
        company_id: int,
        service: EmployeeService = Depends(employee_service),
        # user: User = Depends(superuser)
):
    if service.check_if_exists(company_pk=company_id, user_pk=pk) is None:
        raise NotFoundErrorError(
            detail="Компания с идентификатором %s или сотрудник с идентификатором %s не были найдены."
                   % (company_id, pk),
            status_code=status.HTTP_404_NOT_FOUND
        )
    await service.delete_from_company_by_pk(company_pk=company_id, pk=pk)
