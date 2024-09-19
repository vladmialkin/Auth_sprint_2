from datetime import UTC, datetime, timedelta

from fastapi_users import exceptions, models
from fastapi_users.authentication.strategy import JWTStrategy
from fastapi_users.jwt import decode_jwt, generate_jwt
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.redis import get_redis
from app.models import Session, User
from app.repository.refresh_token import refresh_token_repository
from app.repository.session import session_repository
from app.users.manager import UserManager


class RefreshJWTStrategy(JWTStrategy):
    async def write_token(self, user: models.UP) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "type": "refresh",
        }
        return generate_jwt(
            data,
            self.encode_key,
            self.lifetime_seconds,
            algorithm=self.algorithm,
        )

    async def read_token(
        self,
        token: str | None,
        user_manager: UserManager,
    ) -> User | None:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token,
                self.decode_key,
                self.token_audience,
                algorithms=[self.algorithm],
            )

        except PyJWTError:
            return None

        user_id = data.get("sub")

        if user_id is None:
            return None

        if data.get("type") != "refresh":
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
        except exceptions.InvalidID:
            return None

        stored_refresh_token = await refresh_token_repository.get(
            user_manager.user_db.session, token=token
        )

        if stored_refresh_token.expiration_date < datetime.now(UTC).replace(
            tzinfo=None
        ):
            return None

        return await user_manager.get(parsed_id)

    async def create_session(
        self,
        token: str,
        user_agent: str,
        user: User,
        db_session: AsyncSession,
    ):
        current_session = await session_repository.get(
            db_session,
            user_id=user.id,
            user_agent=user_agent,
            options=[joinedload(Session.refresh_token)],
        )

        if current_session is not None:
            # TODO: вынести в отдельный метод
            await refresh_token_repository.update(
                db_session,
                current_session.refresh_token,
                {"expiration_date": datetime.now(UTC).replace(tzinfo=None)},
            )

        stored_refresh_token = await refresh_token_repository.create(
            db_session,
            data={
                "token": token,
                "expiration_date": datetime.now(UTC).replace(tzinfo=None)
                + timedelta(seconds=self.lifetime_seconds),
            },
            commit=False,
        )
        await session_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "refresh_token_id": stored_refresh_token.id,
                "user_agent": user_agent,
            },
        )

    async def prolong_session(
        self, user: User, user_agent: str, db_session: AsyncSession
    ) -> None:
        session: Session = await session_repository.get(
            db_session,
            user_id=user.id,
            user_agent=user_agent,
            options=[joinedload(Session.refresh_token)],
        )

        await refresh_token_repository.update(
            db_session,
            session.refresh_token,
            {
                "expiration_date": datetime.now(UTC).replace(tzinfo=None)
                + timedelta(seconds=self.lifetime_seconds)
            },
        )

    async def destroy_token(
        self, db_session: AsyncSession, user: User, user_agent: str
    ) -> None:
        session = await session_repository.get(
            db_session,
            user_id=user.id,
            user_agent=user_agent,
            options=[joinedload(Session.refresh_token)],
        )

        await refresh_token_repository.update(
            db_session,
            session.refresh_token,
            {
                "expiration_date": datetime.now(UTC).replace(tzinfo=None),
            },
        )


class AccessJWTStrategy(JWTStrategy):
    async def write_token(self, user: models.UP) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "type": "access",
        }
        return generate_jwt(
            data,
            self.encode_key,
            self.lifetime_seconds,
            algorithm=self.algorithm,
        )

    async def read_token(
        self, token: str | None, user_manager: UserManager
    ) -> User | None:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token,
                self.decode_key,
                self.token_audience,
                algorithms=[self.algorithm],
            )

        except PyJWTError:
            return None

        user_id = data.get("sub")

        if user_id is None:
            return None

        if data.get("type") != "access":
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
        except exceptions.InvalidID:
            return None

        redis_conn = await get_redis()
        if await redis_conn.exists(f"blacklisted_access_token:{token}"):
            return None

        return await user_manager.get(parsed_id)

    async def destroy_token(self, token: str) -> None:
        token_data = decode_jwt(
            token,
            self.decode_key,
            self.token_audience,
            algorithms=[self.algorithm],
        )
        ttl = token_data.get("exp") - int(datetime.now(UTC).timestamp())

        redis_conn = await get_redis()
        await redis_conn.set(f"blacklisted_access_token:{token}", "", ex=ttl)
