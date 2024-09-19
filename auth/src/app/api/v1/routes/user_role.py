from fastapi import APIRouter, HTTPException, status

from app.api.deps.roles import ForAdminOnly
from app.api.deps.session import Session
from app.api.v1.schemas.user_role import (
    UserRoleCreateSchema,
    UserRoleRetrieveSchema,
    UserRoleRevokeSchema,
)
from app.repository.role import role_repository
from app.repository.user import user_repository
from app.repository.user_role import user_role_repository

router = APIRouter()


@router.post("/create")
async def set_role(
    _: ForAdminOnly, session: Session, data: UserRoleCreateSchema
) -> UserRoleRetrieveSchema:
    """Назначить роль пользователю."""

    role_is_exists = await role_repository.exists(session, id=data.role_id)

    if not role_is_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    user_is_exists = await user_repository.exists(session, id=data.user_id)

    if not user_is_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_role_data = {"user_id": data.user_id, "role_id": data.role_id}

    return await user_role_repository.create(session, user_role_data)


@router.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_role(
    _: ForAdminOnly, session: Session, data: UserRoleRevokeSchema
) -> None:
    """Отозвать роль пользователя."""

    role_is_exists = await role_repository.exists(session, id=data.role_id)

    if not role_is_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    user_is_exists = await user_repository.exists(session, id=data.user_id)

    if not user_is_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_role = await user_role_repository.get(
        session, user_id=data.user_id, role_id=data.role_id
    )

    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesnt have this role",
        )

    return await user_role_repository.delete(session, user_role)
