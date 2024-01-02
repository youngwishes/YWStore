from fastapi import APIRouter, status, Depends
from fastapi_users.exceptions import UserAlreadyExists

from src.core.exceptions import UniqueConstraintError
from src.core.http_response_schemas import UniqueConstraint, Unauthorized
from src.core.users.auth import current_user
from src.core.users.depends import get_user_service
from src.core.users.manager import UserService
from src.core.users.models import User
from src.core.users.schemas import UserCreate, UserRead, UserUpdate

users_router = APIRouter()


@users_router.post(
    "",
    response_model=UserRead,
    responses={
        status.HTTP_201_CREATED: {"model": UserRead},
        status.HTTP_400_BAD_REQUEST: {"model": UniqueConstraint},
    },
    description="Зарегистрировать нового пользователя",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: UserCreate,
    manager: UserService = Depends(get_user_service),
) -> UserRead:
    try:
        return await manager.create(user_create=user, safe=True)
    except UserAlreadyExists:
        raise UniqueConstraintError(
            detail="Пользователь с почтой <%s>  уже зарегистрирован в системе."
            % user.email,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


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
    manager: UserService = Depends(get_user_service),
    user: User = Depends(current_user),
):
    await manager.delete(await manager.get(id=user.id))


@users_router.patch(
    "/",
    description="Частично обновить учетные данные пользователя",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": UserUpdate},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_400_BAD_REQUEST: {"model": UniqueConstraint},
    },
    response_model=UserRead,
)
async def user_edit(
    user_to_update: UserUpdate,
    manager: UserService = Depends(get_user_service),
    user: User = Depends(current_user),
) -> UserRead:
    try:
        return await manager.update(
            user_update=user_to_update,
            user=await manager.get(user.id),
            safe=True,
        )
    except UserAlreadyExists:
        raise UniqueConstraintError(
            detail="Пользователь с почтой <%s>  уже зарегистрирован в системе."
            % user.email,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@users_router.get(
    "/me",
    description="Получение информации о текущем пользователе.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_200_OK: {"model": UserRead},
    },
    response_model=UserRead,
)
async def get_user(
    manager: UserService = Depends(get_user_service),
    user: User = Depends(current_user),
) -> UserRead:
    return await manager.get(user.id)
