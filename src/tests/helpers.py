from __future__ import annotations
from typing import TYPE_CHECKING, Any
from sqlalchemy.sql import func, select

if TYPE_CHECKING:
    from httpx import Response, AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


async def make_post_request(
    async_client: AsyncClient,
    url: str,
    json: dict,
) -> Response:
    async with async_client as client:
        response = await client.post(url=url, json=json)
    return response


async def get_objects_count(model: Any, session: AsyncSession) -> int:
    count = await session.execute(func.count(model.id))
    return count.scalar_one()


async def get_object(model: Any, session: AsyncSession) -> Any:
    result = await session.execute(select(model))
    return result.scalar_one_or_none()
