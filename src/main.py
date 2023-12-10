from fastapi import FastAPI
from src.core.users.auth import (
    auth_router,
    register_router,
    users_router,
)
from src.core.config import get_settings
from src.apps.company.routes import company_router
from src.apps.employee.routes import employee_router

description = """
# Статус - в разработке ⚙️

## Краткое описание 📃

* ### Данное API предназначено для реализации функционала онлайн-платформы, которая представляет из себя **магазин одежды**👕
* ### Функционал предусматривает:
\t- **размещение одежды брендов на платформе**✅
\t- **управление ассортиментом**✅
\t- **оформление заказа по конкретной позиции**✅
\t- **корзина, рейтинг компаний и т.д.**✅

* ### Сервис подходит для **высоких нагрузок** и может работать с большим кол-вом пользователей одновременно🐫
"""


settings = get_settings()


class YWStoreAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.router.prefix = settings.BASE_API_PREFIX


app = YWStoreAPI(
    debug=settings.DEBUG,
    description=description,
    title=settings.PROJECT_NAME,
    docs_url=settings.BASE_API_PREFIX + "/docs",
    version=str(settings.API_VERSION_INT) + ".0",
    contact={
        "name": "Danil Fedorov",
        "url": "https://t.me/youngWishes",
        "email": "mysc1@yandex.ru",
    },
)

app.include_router(auth_router, tags=["/auth"], prefix="/auth/jwt")
app.include_router(register_router, tags=["/auth"], prefix="/auth")
app.include_router(users_router, tags=["/users"], prefix="/users")
app.include_router(company_router, tags=["/company"], prefix="/company")
app.include_router(employee_router, tags=["/employees"], prefix="/employees")
