from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session
from app.repository.base import SQLAlchemyRepository


class SessionRepository(SQLAlchemyRepository[Session]):
    async def get_history(
        self, session: AsyncSession, user_id: UUID
    ) -> list[Session]:
        query = (
            select(self._model)
            .filter_by(user_id=user_id)
            .order_by(Session.created_at.desc())
        )
        return (await session.execute(query)).scalars().all()


session_repository = SessionRepository(Session)
