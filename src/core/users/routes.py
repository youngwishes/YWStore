from fastapi import APIRouter, status, Depends
from fastapi_users.exceptions import UserNotExists, UserAlreadyExists

from src.core.exceptions import UniqueConstraintError, NotFoundError
from src.core.http_response_schemas import UniqueConstraint, NotFound, Unauthorized
from src.core.users.auth import current_user
from src.core.users.depends import get_user_manager
from src.core.users.manager import UserManager
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
    manager: UserManager = Depends(get_user_manager),
) -> UserRead:
    try:
        return await manager.create(user_create=user, safe=True)
    except UserAlreadyExists:
        raise UniqueConstraintError(
            detail="Пользователь с этими данными уже зарегестрирован в системе.",
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
    manager: UserManager = Depends(get_user_manager),
    _: User = Depends(current_user),
):
    await manager.delete(await manager.get(id=_.id))


@users_router.put(
    "/{user_id}",
    description="Обновить учетные данные пользователя",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": UserUpdate},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
    },
)
async def user_edit(
    user_id: int,
    user: UserUpdate,
    manager: UserManager = Depends(get_user_manager),
    _: User = Depends(current_user),
) -> UserRead:
    try:
        currently_user = await manager.get(id=user_id)
    except UserNotExists:
        raise NotFoundError(
            detail="Пользователь с идентификатором %s не был найден" % user_id,
            status_code=404,
        )
    return await manager.update(user_update=user, user=currently_user, safe=True)


@users_router.get(
    "/@me",
    description="Получение информации о текущем пользователе.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_200_OK: {"model": UserRead},
    },
    response_model=UserRead,
)
async def get_user(
    manager: UserManager = Depends(get_user_manager),
    _: User = Depends(current_user),
) -> UserRead:
    return await manager.get(_.id)
