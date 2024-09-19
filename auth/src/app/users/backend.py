from fastapi import Response, status
from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.strategy import JWTStrategy
from fastapi_users.authentication.transport import (
    Transport,
    TransportLogoutNotSupportedError,
)
from fastapi_users.types import DependencyCallable
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.users.schemas import BearerResponseSchema, RefreshResponseSchema
from app.users.strategy import AccessJWTStrategy, RefreshJWTStrategy


class RefreshableAuthenticationBackend(AuthenticationBackend):
    def __init__(
        self,
        name: str,
        transport: Transport,
        get_access_strategy: DependencyCallable[
            JWTStrategy[models.UP, models.ID]
        ],
        get_refresh_strategy: DependencyCallable[
            JWTStrategy[models.UP, models.ID]
        ],
    ):
        super().__init__(name, transport, get_access_strategy)
        self.get_refresh_strategy = get_refresh_strategy

    async def login(
        self,
        access_strategy: AccessJWTStrategy,
        refresh_strategy: RefreshJWTStrategy,
        user: User,
        db_session: AsyncSession,
        user_agent: str | None = None,
    ) -> BearerResponseSchema:
        access_token = await access_strategy.write_token(user)
        refresh_token = await refresh_strategy.write_token(user)

        await refresh_strategy.create_session(
            refresh_token,
            user_agent,
            user,
            db_session,
        )

        return BearerResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(
        self,
        access_strategy: AccessJWTStrategy,
        refresh_strategy: RefreshJWTStrategy,
        user: User,
        db_session: AsyncSession,
        user_agent: str | None = None,
    ) -> RefreshResponseSchema:
        await refresh_strategy.prolong_session(user, user_agent, db_session)

        access_token = await access_strategy.write_token(user)

        return RefreshResponseSchema(
            access_token=access_token,
        )

    async def logout(
        self,
        access_strategy: AccessJWTStrategy,
        refresh_strategy: RefreshJWTStrategy,
        db_session: AsyncSession,
        token: str,
        user: User,
        user_agent: str | None = None,
    ) -> Response:
        await refresh_strategy.destroy_token(db_session, user, user_agent)
        await access_strategy.destroy_token(token)

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response
