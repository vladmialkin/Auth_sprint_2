from uuid import UUID

from app.api.v1.schemas.base import Base


class UserRoleBaseSchema(Base):
    user_id: UUID
    role_id: UUID


class UserRoleCreateSchema(UserRoleBaseSchema):
    pass


class UserRoleRevokeSchema(UserRoleBaseSchema):
    pass


class UserRoleRetrieveSchema(UserRoleBaseSchema):
    pass
