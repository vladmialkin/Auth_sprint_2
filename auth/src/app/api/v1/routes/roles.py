from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps.roles import ForAdminOnly
from app.api.deps.session import Session
from app.api.v1.schemas.role import (
    RoleCreateSchema,
    RoleRetrieveSchema,
    RoleUpdateSchema,
)
from app.repository.role import role_repository

router = APIRouter()


@router.get("/")
async def retrieve_all(
    _: ForAdminOnly,
    session: Session,
) -> list[RoleRetrieveSchema]:
    """Просмотр всех ролей."""

    return await role_repository.filter(session)


@router.post("/")
async def create(
    _: ForAdminOnly, session: Session, data: RoleCreateSchema
) -> RoleRetrieveSchema:
    """Создание роли."""
    is_exist = await role_repository.exists(session, name=data.name)

    if is_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    return await role_repository.create(session, data={"name": data.name})


@router.get("/{role_id}")
async def retrive(
    _: ForAdminOnly, session: Session, role_id: UUID
) -> RoleRetrieveSchema:
    """Получение информации о роли."""

    role = await role_repository.get(session, id=role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(_: ForAdminOnly, session: Session, role_id: UUID) -> None:
    """Удаление роли."""

    role = await role_repository.get(session, id=role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    await role_repository.delete(session, role)


@router.put("/{role_id}")
async def update(
    _: ForAdminOnly,
    session: Session,
    data: RoleUpdateSchema,
    role_id: UUID,
) -> RoleRetrieveSchema:
    """Изменение роли."""

    role = await role_repository.get(session, id=role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    new_role = await role_repository.update(session, role, {"name": data.name})

    return new_role
