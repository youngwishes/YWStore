from __future__ import annotations
from typing import Sequence, TYPE_CHECKING
from fastapi import APIRouter, Depends, Body, status
from src.apps.roles.controller import RoleController
from src.apps.roles.enums import CompanyRoles
from src.apps.roles.schemas import RoleIn, RoleOut
from src.apps.roles.depends import get_role_controller
from src.core.http_response_schemas import NotFound, Unauthorized, NotAllowed
from src.core.auth.strategy import superuser, current_user
from src.apps.users.schemas import UserOut

if TYPE_CHECKING:
    from src.apps.users.models import Role, User


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
    controller: RoleController = Depends(get_role_controller),
    _: User = Depends(superuser),
) -> Role:
    return await controller.create(in_model=role)


@roles_router.delete(
    "/{role_pk}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_201_CREATED: {"model": RoleOut},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def delete_role(
    role_pk: int,
    controller: RoleController = Depends(get_role_controller),
    _: User = Depends(superuser),
):
    await controller.delete_role(role_pk=role_pk)


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
    controller: RoleController = Depends(get_role_controller),
    _: User = Depends(superuser),
):
    await controller.delete()


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
    controller: RoleController = Depends(get_role_controller),
    _: User = Depends(current_user),
) -> Sequence[Role]:
    return await controller.get()


@roles_router.put(
    "/{role_pk}",
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
    role_pk: int,
    new_name: str = Body(embed=True),
    controller: RoleController = Depends(get_role_controller),
    _: User = Depends(superuser),
) -> Role:
    return await controller.update(role_pk=role_pk, new_name=new_name, partial=False)


@roles_router.post(
    "/{user_pk}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": UserOut},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": NotAllowed},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Роли нет среди доступных",
        },
    },
)
async def add_role_to_user(
    user_pk: int,
    roles_list: Sequence[CompanyRoles] = Body(embed=True),
    controller: RoleController = Depends(get_role_controller),
    _: User = Depends(superuser),
) -> User:
    return await controller.add_roles_to_user(user_pk=user_pk, roles_list=roles_list)
