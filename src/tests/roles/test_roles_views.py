from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from fastapi import status
from src.core.users.models import Role
from src.tests.defaults import TEST_ROLE_NEW_NAME, TEST_ROLE_NAME
from src.tests.helpers import check_object_data, get_objects_count, get_object

from src.main import app

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_role_creation(init_role_data: dict, async_client: AsyncClient):
    """Добавление новой роли неавторизованным пользователем"""
    url = app.url_path_for("create_new_role")
    response = await async_client.post(url, json=init_role_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_role_creation_authorized(
    init_role_data: dict,
    authorized_client: AsyncClient,
):
    """Добавление новой роли авторизованным пользователем"""
    url = app.url_path_for("create_new_role")
    response = await authorized_client.post(url, json=init_role_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_role_creation_superuser(
    init_role_data: dict,
    superuser_client: AsyncClient,
    session: AsyncSession,
):
    """Добавление новой роли супер-юзером"""
    objects_count_before = await get_objects_count(model=Role, session=session)
    url = app.url_path_for("create_new_role")
    response = await superuser_client.post(url, json=init_role_data)
    assert response.status_code == status.HTTP_201_CREATED
    objects_count_after = await get_objects_count(model=Role, session=session)
    assert objects_count_before == objects_count_after - 1
    instance = await get_object(Role, session)
    assert await check_object_data(obj=instance, data=init_role_data)


@pytest.mark.anyio
async def test_role_update(
    create_role: Role,
    async_client: AsyncClient,
    session: AsyncSession,
):
    """Обновление существующей роли неавторизованным пользователем"""
    url = app.url_path_for("update_role", old_name=create_role.name)
    response = await async_client.put(url, json={"new_name": TEST_ROLE_NEW_NAME})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    instance = await get_object(model=Role, session=session)
    assert instance.name == create_role.name == TEST_ROLE_NAME


@pytest.mark.anyio
async def test_role_update_authorized(
    create_role: Role,
    authorized_client: AsyncClient,
    session: AsyncSession,
):
    """Обновление существующей роли авторизованным пользователем"""
    url = app.url_path_for("update_role", old_name=create_role.name)
    response = await authorized_client.put(url, json={"new_name": TEST_ROLE_NEW_NAME})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    instance = await get_object(model=Role, session=session)
    assert instance.name == create_role.name == TEST_ROLE_NAME


@pytest.mark.anyio
async def test_role_update_superuser(
    create_role: Role,
    superuser_client: AsyncClient,
    session: AsyncSession,
):
    """Обновление существующей роли супер-юзером"""
    assert create_role.name == TEST_ROLE_NAME
    url = app.url_path_for("update_role", old_name=create_role.name)
    response = await superuser_client.put(url, json={"new_name": TEST_ROLE_NEW_NAME})
    assert response.status_code == status.HTTP_200_OK
    instance = await get_object(model=Role, session=session)
    assert instance.name == TEST_ROLE_NEW_NAME != TEST_ROLE_NAME


@pytest.mark.anyio
async def test_role_delete(
    create_role: Role,
    async_client: AsyncClient,
    session: AsyncSession,
):
    """Удаление существующей роли неавторизованным пользователем"""
    roles_count_before = await get_objects_count(model=Role, session=session)
    url = app.url_path_for("delete_role", role_name=create_role.name)
    response = await async_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    roles_count_after = await get_objects_count(model=Role, session=session)
    assert roles_count_after == roles_count_before


@pytest.mark.anyio
async def test_role_delete_authorized(
    create_role: Role,
    authorized_client: AsyncClient,
    session: AsyncSession,
):
    """Удаление существующей роли авторизованным пользователем"""
    roles_count_before = await get_objects_count(model=Role, session=session)
    url = app.url_path_for("delete_role", role_name=create_role.name)
    response = await authorized_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    roles_count_after = await get_objects_count(model=Role, session=session)
    assert roles_count_after == roles_count_before


@pytest.mark.anyio
async def test_role_delete_superuser(
    create_role: Role,
    superuser_client: AsyncClient,
    session: AsyncSession,
):
    """Удаление существующей роли супер-юзером"""
    roles_count_before = await get_objects_count(model=Role, session=session)
    url = app.url_path_for("delete_role", role_name=create_role.name)
    response = await superuser_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    roles_count_after = await get_objects_count(model=Role, session=session)
    assert roles_count_after == roles_count_before - 1


@pytest.mark.anyio
async def test_role_delete_all(
    create_role: Role,
    async_client: AsyncClient,
    session: AsyncSession,
):
    """Удаление всех ролей неавторизованным пользователем"""
    roles_count_before = await get_objects_count(model=Role, session=session)
    url = app.url_path_for("delete_roles")
    response = await async_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    roles_count_after = await get_objects_count(model=Role, session=session)
    assert roles_count_after == roles_count_before


@pytest.mark.anyio
async def test_role_delete_authorized_all(
    create_role: Role,
    authorized_client: AsyncClient,
    session: AsyncSession,
):
    """Удаление всех ролей авторизованным пользователем"""
    roles_count_before = await get_objects_count(model=Role, session=session)
    url = app.url_path_for("delete_roles")
    response = await authorized_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    roles_count_after = await get_objects_count(model=Role, session=session)
    assert roles_count_after == roles_count_before


@pytest.mark.anyio
async def test_role_delete_superuser_all(
    create_role: Role,
    superuser_client: AsyncClient,
    session: AsyncSession,
):
    """Удаление всех ролей супер-юзером"""
    roles_count_before = await get_objects_count(model=Role, session=session)
    assert roles_count_before != 0
    url = app.url_path_for("delete_roles")
    response = await superuser_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    roles_count_after = await get_objects_count(model=Role, session=session)
    assert roles_count_after == roles_count_before - 1 and roles_count_after == 0


@pytest.mark.anyio
async def test_get_roles_list_unauthorized(
    create_role: Role,
    async_client: AsyncClient,
):
    """Вывести список ролей для неавторизованного юзера"""
    url = app.url_path_for("get_roles")
    response = await async_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_get_roles_list_authorized(
    create_role: Role,
    authorized_client: AsyncClient,
):
    """Вывести список ролей для авторизованного юзера"""
    url = app.url_path_for("get_roles")
    response = await authorized_client.get(url)
    assert response.status_code == status.HTTP_200_OK
