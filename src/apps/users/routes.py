from fastapi import APIRouter, status, Depends
from src.apps.users.controller import UserController
from src.core.http_response_schemas import UniqueConstraint, Unauthorized
from src.core.auth.strategy import current_user
from src.apps.users.depends import get_user_controller
from src.apps.users.models import User
from src.apps.users.schemas import UserIn, UserOut, UserUpdate

users_router = APIRouter()


@users_router.post(
    "",
    response_model=UserOut,
    responses={
        status.HTTP_201_CREATED: {"model": UserOut},
        status.HTTP_400_BAD_REQUEST: {"model": UniqueConstraint},
    },
    description="Зарегистрировать нового пользователя",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: UserIn,
    controller: UserController = Depends(get_user_controller),
) -> UserOut:
    return await controller.create(user_data=user)


@users_router.delete(
    "/",
    description="Удалить пользователя",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Пользователь успешно удален."},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_delete(
    controller: UserController = Depends(get_user_controller),
    user: User = Depends(current_user),
):
    await controller.delete(user_pk=user.id)


@users_router.patch(
    "/",
    description="Частично обновить учетные данные пользователя",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": UserUpdate},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_400_BAD_REQUEST: {"model": UniqueConstraint},
    },
    response_model=UserOut,
)
async def user_edit(
    user_to_update: UserUpdate,
    controller: UserController = Depends(get_user_controller),
    user: User = Depends(current_user),
) -> UserOut:
    return await controller.update(data=user_to_update, user_pk=user.id)


@users_router.get(
    "/me",
    description="Получение информации о текущем пользователе.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_200_OK: {"model": UserOut},
    },
    response_model=UserOut,
)
async def get_user(
    controller: UserController = Depends(get_user_controller),
    user: User = Depends(current_user),
) -> UserOut:
    return await controller.get_user_by_pk(user_pk=user.id)
