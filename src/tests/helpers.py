from __future__ import annotations
from typing import TYPE_CHECKING, Any
from sqlalchemy.sql import func, select
from httpx import Response, AsyncClient

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def make_post_request(
    async_client: AsyncClient,
    url: str,
    json: dict,
) -> Response:
    """Хелпер для пост-запроса"""
    async with async_client as client:
        response = await client.post(url=url, json=json)
    return response


async def get_objects_count(model: Any, session: AsyncSession) -> int:
    """Хелпер для проверки количества записей в БД"""
    count = await session.execute(func.count(model.id))
    return count.scalar_one()


async def get_object(model: Any, session: AsyncSession) -> Any:
    """Хелпер для получения объекта"""
    result = await session.execute(select(model))
    return result.scalar_one_or_none()


async def check_object_data(obj: Any, data: dict) -> bool:
    """Проверяет, что при создании записи все переданные поля отобразились в базе данных"""
    for key, value in obj.__dict__.items():
        if not key.startswith("_"):
            if sent_value := data.get(key):
                if not sent_value == value:
                    print(
                        f"Sent value is {sent_value}, but in model is {value}",
                    )
                    return False
    return True
