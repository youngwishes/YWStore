from __future__ import annotations
from typing import TYPE_CHECKING, Sequence

import pytest
from fastapi import status

from src.main import app
from src.apps.roles.enums import CompanyRoles
from src.tests.defaults import TEST_ROLE_NEW_NAME, TEST_ROLE_NAME
from src.tests.helpers import check_object_data, get_objects_count, get_object
from src.core.users.models import Role

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.core.users.models import User


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


@pytest.mark.anyio
@pytest.mark.parametrize("role_name", CompanyRoles.list())
async def test_add_new_role_to_user_by_unauthorized(
    role_name: str,
    ywstore_roles: Sequence[Role],
    session: AsyncSession,
    create_test_user: User,
    async_client: AsyncClient,
):
    """Добавление пользователю новой роли от лица не авторизированного юзера."""
    url = app.url_path_for("add_role_to_user", user_pk=create_test_user.id)
    data_to_send = {"roles_list": [role_name]}
    response = await async_client.post(url, json=data_to_send)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        role_name not in [role.name for role in create_test_user.roles]
        and len(create_test_user.roles) == 0
    )


@pytest.mark.anyio
@pytest.mark.parametrize("role_name", CompanyRoles.list())
async def test_add_new_role_to_user_by_authorized(
    role_name: str,
    ywstore_roles: Sequence[Role],
    session: AsyncSession,
    create_test_user: User,
    authorized_client: AsyncClient,
):
    """Добавление пользователю новой роли от лица авторизированного юзера."""
    url = app.url_path_for("add_role_to_user", user_pk=create_test_user.id)
    data_to_send = {"roles_list": [role_name]}
    response = await authorized_client.post(url, json=data_to_send)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        role_name not in [role.name for role in create_test_user.roles]
        and len(create_test_user.roles) == 0
    )


@pytest.mark.anyio
@pytest.mark.parametrize("role_name", CompanyRoles.list())
async def test_add_new_role_to_user_by_superuser(
    role_name: str,
    ywstore_roles: Sequence[Role],
    session: AsyncSession,
    create_test_user: User,
    superuser_client: AsyncClient,
):
    """Добавление пользователю новой роли от лица супер-юзера."""
    url = app.url_path_for("add_role_to_user", user_pk=create_test_user.id)
    data_to_send = {"roles_list": [role_name]}
    response = await superuser_client.post(url, json=data_to_send)
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["roles"][0]["name"] == role_name
    await session.refresh(create_test_user)
    assert role_name in [role.name for role in create_test_user.roles]


@pytest.mark.anyio
async def test_add_new_not_existed_role_to_user_by_superuser(
    ywstore_roles: Sequence[Role],
    session: AsyncSession,
    create_test_user: User,
    superuser_client: AsyncClient,
):
    """Добавление пользователю не существующей в системе роли от лица супер-юзера."""
    url = app.url_path_for("add_role_to_user", user_pk=create_test_user.id)
    data_to_send = {"roles_list": ["Some wrong role name"]}
    response = await superuser_client.post(url, json=data_to_send)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
@pytest.mark.parametrize("role_name", CompanyRoles.list())
async def test_add_new_not_existed_user_by_superuser(
    role_name: str,
    ywstore_roles: Sequence[Role],
    session: AsyncSession,
    create_test_user: User,
    superuser_client: AsyncClient,
):
    """Добавление не существующему пользователю роли от лица супер-юзера."""
    url = app.url_path_for("add_role_to_user", user_pk=1000)
    data_to_send = {"roles_list": [role_name]}
    response = await superuser_client.post(url, json=data_to_send)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_add_many_roles_to_user_by_superuser(
    ywstore_roles: Sequence[Role],
    session: AsyncSession,
    create_test_user: User,
    superuser_client: AsyncClient,
):
    """Добавление пользователю списка ролей от лица супер-юзера."""
    url = app.url_path_for("add_role_to_user", user_pk=create_test_user.id)
    data_to_send = {"roles_list": CompanyRoles.list()}
    response = await superuser_client.post(url, json=data_to_send)
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    user_roles_from_response = [role["name"] for role in user["roles"]]
    await session.refresh(create_test_user)
    user_roles_from_db = [role.name for role in create_test_user.roles]
    for role in CompanyRoles.list():
        assert role in user_roles_from_response
        assert role in user_roles_from_db


@pytest.mark.anyio
async def test_add_exist_role_to_user_by_superuser(
    ywstore_roles: Sequence[Role],
    session: AsyncSession,
    create_test_user: User,
    superuser_client: AsyncClient,
):
    """Добавление пользователю роли в которой он уже состоит от лица супер-юзера."""
    url = app.url_path_for("add_role_to_user", user_pk=create_test_user.id)
    data_to_send = {"roles_list": CompanyRoles.list()}
    response = await superuser_client.post(url, json=data_to_send)
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    user_roles_from_response = [role["name"] for role in user["roles"]]
    await session.refresh(create_test_user)
    user_roles_from_db = [role.name for role in create_test_user.roles]
    for role in CompanyRoles.list():
        assert role in user_roles_from_response
        assert role in user_roles_from_db

    data_to_send = {"roles_list": [CompanyRoles.ADMIN]}
    response = await superuser_client.post(url, json=data_to_send)
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    await session.refresh(create_test_user)
    user_roles_from_response_new = [role["name"] for role in user["roles"]]
    user_roles_from_db_new = [role.name for role in create_test_user.roles]
    for role in user_roles_from_response_new:
        assert role in user_roles_from_response
        assert role in user_roles_from_db_new
