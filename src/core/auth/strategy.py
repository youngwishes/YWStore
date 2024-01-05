from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend,
)

from src.core.config import get_settings
from src.apps.users.depends import _get_user_service
from src.apps.users.models import User
from src.apps.users.schemas import UserOut, UserIn

settings = get_settings()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )


bearer_transport = BearerTransport(
    tokenUrl=settings.BASE_API_PREFIX + "/auth/jwt/login",
)

jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    _get_user_service,
    [jwt_backend],
)

auth_router = fastapi_users.get_auth_router(backend=jwt_backend)
register_router = fastapi_users.get_register_router(UserOut, UserIn)
current_user = fastapi_users.current_user(active=True)
superuser = fastapi_users.current_user(superuser=True)
