from http import HTTPStatus

import pytest

from app.repository.role import role_repository


@pytest.mark.anyio
async def test_create_role(client, session):
    """Создание роли."""

    test_data = {"name": "test_role"}

    async with client as cl:
        response = await cl.post(
            url="http://localhost:8010/api/v1/roles/", json=test_data
        )
        status_code = response.status_code
        body = response.json()

    role = await role_repository.get(session, id=body["id"])
    await role_repository.delete(session, role)

    assert status_code == HTTPStatus.OK
    assert body["name"] == test_data["name"]


@pytest.mark.anyio
async def test_delete_role(client, session):
    """Удаление роли."""

    test_data = {"name": "test_role"}

    role = await role_repository.create(session, test_data)

    async with client as cl:
        response = await cl.delete(
            url=f"http://localhost:8010/api/v1/roles/{role.id}"
        )
        status_code = response.status_code

    assert status_code == HTTPStatus.NO_CONTENT


@pytest.mark.anyio
async def test_get_role_by_id(client, session):
    """Получение информации о роли."""

    test_data = {"name": "test_role"}

    role = await role_repository.create(session, test_data)
    role_id, role_name = role.id, role.name

    async with client as cl:
        response = await cl.get(
            url=f"http://localhost:8010/api/v1/roles/{role_id}"
        )
        status_code = response.status_code
        body = response.json()

    await role_repository.delete(session, role)

    assert status_code == HTTPStatus.OK
    assert body["id"] == str(role_id)
    assert body["name"] == role_name


@pytest.mark.anyio
async def test_get_all_roles(client, session):
    """Просмотр всех ролей."""

    test_data = [
        {"name": "test_role_1"},
        {"name": "test_role_2"},
        {"name": "test_role_3"},
    ]

    created_roles_list = []

    for role in test_data:
        created = await role_repository.create(session, role)
        created_roles_list.append(created)

    async with client as cl:
        response = await cl.get(url="http://localhost:8010/api/v1/roles/")
        status_code = response.status_code
        body = response.json()

    for role in created_roles_list:
        await role_repository.delete(session, role)

    assert status_code == HTTPStatus.OK
    assert len(body) == len(test_data)


@pytest.mark.anyio
async def test_update_role(client, session):
    """Изменение роли."""

    test_data = {"name": "test_role"}
    update_data = {"name": "new_role"}

    role = await role_repository.create(session, test_data)
    role_id, role_name = role.id, role.name

    async with client as cl:
        response = await cl.put(
            url=f"http://localhost:8010/api/v1/roles/{role_id}",
            json=update_data,
        )
        status_code = response.status_code
        body = response.json()

    await role_repository.delete(session, role)

    assert status_code == HTTPStatus.OK
    assert body["name"] == role_name
