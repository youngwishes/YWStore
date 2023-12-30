from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend,
)

from src.core.config import get_settings
from src.core.users.depends import get_user_manager
from src.core.users.models import User
from src.core.users.schemas import UserRead, UserCreate

settings = get_settings()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )


bearer_transport = BearerTransport(
    tokenUrl=settings.BASE_API_PREFIX + "/auth/jwt/login",
)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

auth_router = fastapi_users.get_auth_router(backend=auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
current_user = fastapi_users.current_user()
superuser = fastapi_users.current_user(superuser=True)
