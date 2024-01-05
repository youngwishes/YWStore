from __future__ import annotations
from typing import Sequence, TYPE_CHECKING
from fastapi import APIRouter, status, Depends
from src.apps.employee.depends import get_employee_controller
from src.apps.employee.models import Employee
from src.apps.employee.schemas import (
    EmployeeIn,
    EmployeeOut,
    EmployeeOptional,
)
from src.core.http_response_schemas import (
    NotFound,
    NotAllowed,
    Unauthorized,
    UniqueConstraint,
)
from src.core.auth.strategy import get_superuser
from src.apps.users.models import User

if TYPE_CHECKING:
    from src.apps.employee.controller import EmployeeController


employee_router = APIRouter()


@employee_router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {"model": EmployeeIn},
        status.HTTP_400_BAD_REQUEST: {"model": UniqueConstraint},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeIn,
)
async def add_employee(
    employee: EmployeeIn,
    controller: EmployeeController = Depends(get_employee_controller),
) -> EmployeeOut:
    return await controller.create(in_model=employee)


@employee_router.get(
    "/{company_pk}",
    responses={
        status.HTTP_200_OK: {"model": Sequence[EmployeeOut]},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
    status_code=status.HTTP_200_OK,
    response_model=Sequence[EmployeeOut],
)
async def get_employees(
    company_pk: int,
    controller: EmployeeController = Depends(get_employee_controller),
) -> Sequence[Employee]:
    return await controller.get(company_pk=company_pk)


@employee_router.delete(
    "/{company_pk}/{user_pk}",
    description="Удаление сотрудника.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Сотрудник удален."},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def delete_employee(
    user_pk: int,
    company_pk: int,
    controller: EmployeeController = Depends(get_employee_controller),
    _: User = Depends(get_superuser),
):
    await controller.delete_from_company_by_pk(company_pk=company_pk, user_pk=user_pk)


@employee_router.patch(
    "/{company_pk}/{user_pk}",
    description="Частичное обновление данных сотрудника.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": EmployeeOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
    },
    response_model=EmployeeOut,
)
async def update_employee_partially(
    user_pk: int,
    company_pk: int,
    employee: EmployeeOptional,
    controller: EmployeeController = Depends(get_employee_controller),
    _: User = Depends(get_superuser),
) -> EmployeeOut:
    return await controller.update(
        user_pk=user_pk,
        company_pk=company_pk,
        data=employee,
        partial=True,
    )
