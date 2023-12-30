from fastapi import APIRouter, status, Depends
from fastapi_users.exceptions import UserNotExists

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
    response_model=UserCreate,
    responses={
        status.HTTP_201_CREATED: {"model": UserCreate},
        status.HTTP_400_BAD_REQUEST: {"model": UniqueConstraint},
    },
    description="Зарегистрировать нового пользователя",
)
async def register_user(
    user: UserCreate,
    manager: UserManager = Depends(get_user_manager),
) -> UserCreate:
    if await manager.get_by_email(user_email=user.email):
        raise UniqueConstraintError(
            detail="Пользователь с емайлом <%s> уже зарегестрирован в системе."
            % user.email,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return await manager.create(user_create=user)


@users_router.get(
    "/{user_id}",
    description="Получить пользователя по идентификатору.",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": UserRead},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
    },
)
async def users_by_id(
    user_id: int,
    manager: UserManager = Depends(get_user_manager),
) -> UserRead:
    try:
        return await manager.get(id=user_id)
    except UserNotExists:
        raise NotFoundError(
            detail="Пользователь с идентификатором %s не был найден" % user_id,
            status_code=404,
        )


@users_router.delete(
    "/{user_id}",
    description="Удалить пользователя",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Пользователь успешно удален."},
        status.HTTP_404_NOT_FOUND: {"model": NotFound},
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_delete(
    user_id: int,
    manager: UserManager = Depends(get_user_manager),
    _: User = Depends(current_user),
):
    try:
        await manager.delete(manager.get(id=user_id))
    except UserNotExists:
        raise NotFoundError(
            detail="Пользователь с идентификатором %s не был найден" % user_id,
            status_code=404,
        )


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
    return await manager.update(user_update=user, user=currently_user)


@users_router.get(
    "/@me",
    description="Получение информации о текущем пользователе.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": Unauthorized},
        status.HTTP_403_FORBIDDEN: {"model": UserRead},
    },
)
async def get_user(
    manager: UserManager = Depends(get_user_manager),
    _: User = Depends(current_user),
) -> UserRead:
    return manager.get(_.id)
