from datetime import datetime
from uuid import UUID

from app.api.v1.schemas.base import Base


class SessionRetrieveSchema(Base):
    id: UUID
    user_agent: str
    created_at: datetime
    updated_at: datetime
