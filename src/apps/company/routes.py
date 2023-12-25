from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
from fastapi import APIRouter, Depends, Body
from src.apps.company.schemas import CompanyIn, CompanyOut, CompanyOptional
from src.core.users.auth import current_user, superuser
from src.apps.company.depends import company_service
from src.core.exceptions import UniqueConstraintError, NotFoundError
from src.core.http_response_schemas import (
    Unauthorized,
    UniqueConstraint,
    NotFound,
    NotAllowed,
)
from src.core.users.models import User
from fastapi import status

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
    _: User = Depends(superuser),
    service: CompanyService = Depends(company_service),
) -> CompanyOut:
    if await service.get_by_name(name=company.name):
        raise UniqueConstraintError(
            detail="Компания с названием <%s> уже зарегистрирована в системе"
            % company.name,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return await service.create(in_model=company)


@company_router.get(
    "",
    response_model=Sequence[CompanyOut],
    description="Получить все компании",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": Sequence[CompanyOut]}},
)
async def companies_list(
    service: CompanyService = Depends(company_service),
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
    service: CompanyService = Depends(company_service),
    _: User = Depends(superuser),
):
    await service.delete()


@company_router.get(
    "/{pk}",
    status_code=status.HTTP_200_OK,
    description="Детальное представление компании",
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def company_detail(
    pk: int,
    service: CompanyService = Depends(company_service),
) -> CompanyOut:
    company = await service.get_by_pk(pk=pk)
    if not company:
        raise NotFoundError(
            detail="Компания с идентификатором %s не была найдена" % pk,
            status_code=404,
        )
    return company


@company_router.delete(
    "/{pk}",
    description="Удалить компанию",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Компания успешно удалена"},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def delete_company(
    pk: int,
    service: CompanyService = Depends(company_service),
    _: User = Depends(superuser),
):
    is_deleted = await service.delete_by_pk(pk=pk)
    if not is_deleted:
        raise NotFoundError(
            detail="Компания с идентификатором %s не была найдена" % pk,
            status_code=404,
        )


@company_router.put(
    "/{pk}",
    description="Обновить учетные данные компании",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def update_company(
    pk: int,
    company: CompanyIn,
    service: CompanyService = Depends(company_service),
    user: User = Depends(current_user),
) -> CompanyOut:
    company_exists = await service.get_by_pk(pk=pk)
    if not company_exists:
        raise NotFoundError(
            detail="Компания с идентификатором %s не была найдена" % pk,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if await service.get_by_name(name=company.name):
        raise UniqueConstraintError(
            detail="Компания с названием <%s> уже зарегистрирована в системе"
            % company.name,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    updated_company = await service.update(pk=pk, data=company)
    return updated_company


@company_router.patch(
    "/{pk}",
    description="Обновить учетные данные компании частично",
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def update_company_partially(
    pk: int,
    company: CompanyOptional,
    service: CompanyService = Depends(company_service),
    _: User = Depends(current_user),
) -> CompanyOut:
    company_exists = await service.get_by_pk(pk=pk)
    if not company_exists:
        raise NotFoundError(
            detail="Компания с идентификатором %s не была найдена" % pk,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if await service.get_by_name(name=company.name):
        raise UniqueConstraintError(
            detail="Компания с названием <%s> уже зарегистрирована в системе"
            % company.name,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    updated_company = await service.update(pk=pk, data=company, partial=True)
    return updated_company


@company_router.patch(
    "/{pk}/verify",
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
    },
)
async def verify_company(
    pk: int,
    is_verified: bool = Body(default=True, embed=True),
    _: User = Depends(superuser),
    service: CompanyService = Depends(company_service),
) -> CompanyOut:
    company = await service.update_is_verified(pk=pk, is_verified=is_verified)
    if not company:
        raise NotFoundError(
            detail="Компания с идентификатором %s не была найдена" % pk,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return company


@company_router.patch(
    "/{pk}/hide",
    responses={
        status.HTTP_200_OK: {"model": CompanyOut},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
    },
)
async def hide_company(
    pk: int,
    is_hidden: bool = Body(default=True, embed=True),
    _: User = Depends(superuser),
    service: CompanyService = Depends(company_service),
) -> CompanyOut:
    company = await service.update_is_hidden(pk=pk, is_hidden=is_hidden)
    if not company:
        raise NotFoundError(
            detail="Компания с идентификатором %s не была найдена" % pk,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return company
