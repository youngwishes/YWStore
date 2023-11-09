from __future__ import annotations
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.anyio
async def test_diploma_is_started(async_client: AsyncClient):
    async with async_client as client:
        response = await client.get("/")
    assert response.status_code == 200
