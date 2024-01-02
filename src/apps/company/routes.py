from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
from fastapi import APIRouter, Depends, Body, status
from src.apps.company.schemas import CompanyIn, CompanyOut, CompanyOptional
from src.apps.roles.enums import CompanyRoles
from src.core.users.auth import current_user, superuser
from src.apps.company.depends import get_company_service
from src.permissions.utils import permissions
from src.core.http_response_schemas import (
    Unauthorized,
    UniqueConstraint,
    NotFound,
    NotAllowed,
)
from src.core.users.models import User
from src.apps.company.validators import is_current_company_admin

if TYPE_CHECKING:
    from src.apps.company.service import CompanyService

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
    service: CompanyService = Depends(get_company_service),
    _: User = Depends(superuser),
) -> CompanyOut:
    return await service.create(in_model=company)


@company_router.get(
    "",
    response_model=Sequence[CompanyOut],
    description="Получить все компании",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": Sequence[CompanyOut]}},
)
async def companies_list(
    service: CompanyService = Depends(get_company_service),
) -> Sequence[CompanyOut]:
    return await service.get()


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
    service: CompanyService = Depends(get_company_service),
    _: User = Depends(superuser),
):
    await service.delete()


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
    service: CompanyService = Depends(get_company_service),
) -> CompanyOut:
    return await service.get_company_or_404(company_pk=company_pk)


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
    service: CompanyService = Depends(get_company_service),
    _: User = Depends(superuser),
):
    await service.delete_by_pk(company_pk=company_pk)


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
@permissions(allowed_roles=[CompanyRoles.ADMIN], validators=[is_current_company_admin])
async def update_company(
    company_pk: int,
    company: CompanyIn,
    service: CompanyService = Depends(get_company_service),
    _: User = Depends(current_user),
) -> CompanyOut:
    return await service.update(company_pk=company_pk, data=company, partial=False)


@company_router.patch(
    "/{company_pk}",
    description="Обновить учетные данные компании частично",
    response_model=CompanyOut,
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
@permissions(allowed_roles=[CompanyRoles.ADMIN], validators=[is_current_company_admin])
async def update_company_partially(
    company_pk: int,
    company: CompanyOptional,
    service: CompanyService = Depends(get_company_service),
    _: User = Depends(current_user),
) -> CompanyOut:
    return await service.update(company_pk=company_pk, data=company, partial=True)


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
    _: User = Depends(superuser),
    service: CompanyService = Depends(get_company_service),
) -> CompanyOut:
    return await service.update_is_verified(
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
    _: User = Depends(superuser),
    service: CompanyService = Depends(get_company_service),
) -> CompanyOut:
    return await service.update_is_hidden(company_pk=company_pk, is_hidden=is_hidden)
