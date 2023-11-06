from fastapi import FastAPI, Depends
from src.core.users.auth import auth_router, register_router, fastapi_users
from src.core.users.models import User
from src.core.config import get_settings


settings = get_settings()


class YshopAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.router.prefix = settings.BASE_API_PREFIX


app = YshopAPI(
    debug=settings.DEBUG,
    description="Online shop",
    title=settings.PROJECT_NAME,
)

app.include_router(auth_router, tags=["/auth"], prefix="/auth/jwt")
app.include_router(register_router, tags=["/auth"], prefix="/auth")

current_user = fastapi_users.current_user()


@app.get("/protected-route")
async def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.email}"


@app.get("/")
async def index():
    return {"diploma": "started"}
