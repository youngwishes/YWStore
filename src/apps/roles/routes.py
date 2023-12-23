from __future__ import annotations
from typing import Sequence
from fastapi import APIRouter, Depends, Body
from src.apps.roles.service import RoleService
from src.apps.roles.shemas import RoleIn, RoleOut
from src.apps.roles.depends import user_role_service
from src.core.exceptions import NotFoundError, UniqueConstraintError
from src.core.http_response_schemas import NotFound, Unauthorized, NotAllowed
from src.core.users.auth import superuser, current_user
from src.core.users.models import Role, User
from fastapi import status

roles_router = APIRouter()


@roles_router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {"model": RoleOut},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_role(
    role: RoleIn,
    service: RoleService = Depends(user_role_service),
    user: User = Depends(superuser),
) -> Role:
    if not await service.get_by_name(name=role.name):
        return await service.create(in_model=role)
    raise UniqueConstraintError(
        detail="Роль с названием %s уже существует в системе" % role.name,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@roles_router.delete(
    "/{role_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_201_CREATED: {"model": RoleOut},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def delete_role(
    role_name: str,
    service: RoleService = Depends(user_role_service),
    user: User = Depends(superuser),
):
    if not await service.delete_role(name=role_name):
        raise NotFoundError(
            detail="Роль с названием %s не была найдена в системе" % role_name,
            status_code=status.HTTP_404_NOT_FOUND,
        )


@roles_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Роли успешно удалены из системы"},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
    },
)
async def delete_roles(
    service: RoleService = Depends(user_role_service),
    user: User = Depends(superuser),
):
    await service.delete()


@roles_router.get(
    "",
    response_model=Sequence[RoleOut],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": Sequence[RoleOut]},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
    },
)
async def get_roles(
    service: RoleService = Depends(user_role_service),
    user: User = Depends(current_user),
) -> Sequence[Role]:
    return await service.get()


@roles_router.put(
    "/{old_name}",
    response_model=RoleOut,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": RoleOut},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def update_role(
    old_name: str,
    new_name: str = Body(embed=True),
    service: RoleService = Depends(user_role_service),
    user: User = Depends(superuser),
):
    if updated_role := await service.update(old_name=old_name, new_name=new_name):
        return updated_role
    raise NotFoundError(
        detail="Роль с названием %s не была найдена в системе" % old_name,
        status_code=status.HTTP_404_NOT_FOUND,
    )
