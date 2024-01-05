from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
from fastapi import APIRouter, Depends, Body, status

from src.apps.company.schemas import CompanyIn, CompanyOut, CompanyOptional
from src.core.auth.strategy import get_superuser
from src.apps.company.depends import get_company_controller
from src.core.exceptions import IsOwnerError
from src.apps.roles.access import get_company_admin
from src.core.http_response_schemas import (
    Unauthorized,
    UniqueConstraint,
    NotFound,
    NotAllowed,
)
from src.apps.users.models import User

if TYPE_CHECKING:
    from src.apps.company.controller import CompanyController

company_router = APIRouter()


@company_router.post(
    "",
    response_model=CompanyOut,
    responses={
        status.HTTP_201_CREATED: {"model": CompanyOut},
        status.HTTP_400_BAD_REQUEST: {"model": UniqueConstraint},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
    },
    status_code=status.HTTP_201_CREATED,
    description="Зарегистрировать новую компанию",
)
async def register_company(
    company: CompanyIn,
    controller: CompanyController = Depends(get_company_controller),
    _: User = Depends(get_superuser),
) -> CompanyOut:
    return await controller.create(in_model=company)


@company_router.get(
    "",
    response_model=Sequence[CompanyOut],
    description="Получить все компании",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": Sequence[CompanyOut]}},
)
async def companies_list(
    controller: CompanyController = Depends(get_company_controller),
) -> Sequence[CompanyOut]:
    return await controller.get()


@company_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удалить все компании",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": None},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
    },
)
async def delete_companies(
    controller: CompanyController = Depends(get_company_controller),
    _: User = Depends(get_superuser),
):
    await controller.delete()


@company_router.get(
    "/{company_pk}",
    status_code=status.HTTP_200_OK,
    description="Детальное представление компании",
    response_model=CompanyOut,
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def company_detail(
    company_pk: int,
    controller: CompanyController = Depends(get_company_controller),
) -> CompanyOut:
    return await controller.get_company_or_404(company_pk=company_pk)


@company_router.delete(
    "/{company_pk}",
    description="Удалить компанию",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Компания успешно удалена"},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def delete_company(
    company_pk: int,
    controller: CompanyController = Depends(get_company_controller),
    _: User = Depends(get_superuser),
):
    await controller.delete_by_pk(company_pk=company_pk)


@company_router.put(
    "/{company_pk}",
    description="Обновить учетные данные компании",
    status_code=status.HTTP_200_OK,
    response_model=CompanyOut,
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def update_company(
    company_pk: int,
    company: CompanyIn,
    controller: CompanyController = Depends(get_company_controller),
    admin: User = Depends(get_company_admin),
) -> CompanyOut:
    if not admin.employee.company_id == company_pk:
        raise IsOwnerError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не имеете доступа к данной компании.",
        )
    return await controller.update(company_pk=company_pk, data=company, partial=False)


@company_router.patch(
    "/{company_pk}",
    description="Обновить учетные данные компании частично",
    response_model=CompanyOut,
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def update_company_partially(
    company_pk: int,
    company: CompanyOptional,
    controller: CompanyController = Depends(get_company_controller),
    admin: User = Depends(get_company_admin),
) -> CompanyOut:
    if not admin.employee.company_id == company_pk:
        raise IsOwnerError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не имеете доступа к данной компании.",
        )
    return await controller.update(company_pk=company_pk, data=company, partial=True)


@company_router.patch(
    "/{company_pk}/verify",
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
    },
)
async def verify_company(
    company_pk: int,
    is_verified: bool = Body(default=True, embed=True),
    _: User = Depends(get_superuser),
    controller: CompanyController = Depends(get_company_controller),
) -> CompanyOut:
    return await controller.update_is_verified(
        company_pk=company_pk,
        is_verified=is_verified,
    )


@company_router.patch(
    "/{company_pk}/hide",
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
    },
)
async def hide_company(
    company_pk: int,
    is_hidden: bool = Body(default=True, embed=True),
    _: User = Depends(get_superuser),
    controller: CompanyController = Depends(get_company_controller),
) -> CompanyOut:
    return await controller.update_is_hidden(company_pk=company_pk, is_hidden=is_hidden)
