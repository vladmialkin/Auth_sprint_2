from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime


class UserRetrieveSchema(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)
