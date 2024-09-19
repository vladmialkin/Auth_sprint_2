from datetime import datetime
from uuid import UUID

from app.api.v1.schemas.base import Base


class RoleBaseSchema(Base):
    name: str


class RoleCreateSchema(RoleBaseSchema): ...


class RoleUpdateSchema(RoleBaseSchema): ...


class RoleRetrieveSchema(RoleBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
