from datetime import datetime
from uuid import UUID

from fastapi_users import schemas


class UserCreateSchema(schemas.BaseUserCreate):
    pass


class UserUpdateSchema(schemas.BaseUserUpdate):
    pass


class UserRetrieveSchema(schemas.BaseUser[UUID]):
    created_at: datetime
    updated_at: datetime
