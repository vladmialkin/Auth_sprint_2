from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import FastAPIUsers, exceptions
from fastapi_users.db import SQLAlchemyUserDatabase

from app.api.deps.session import Session
from app.models import OAuthAccount, User
from app.settings.api import settings as api_settings
from app.settings.jwt import settings as jwt_settings
from app.users.backend import RefreshableAuthenticationBackend
from app.users.manager import UserManager as _UserManager
from app.users.schemas import RefreshTokenSchema
from app.users.strategy import AccessJWTStrategy, RefreshJWTStrategy
from app.users.transport import RefreshableBearerTransport


async def get_user_db(
    session: Session,
) -> AsyncGenerator[SQLAlchemyUserDatabase, None, None]:
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[_UserManager, None, None]:
    yield _UserManager(user_db)


def get_access_jwt_strategy() -> AccessJWTStrategy:
    return AccessJWTStrategy(
        secret=api_settings.SECRET_KEY,
        lifetime_seconds=jwt_settings.ACCESS_TOKEN_LIFETIME_SECONDS,
    )


def get_refresh_jwt_strategy() -> RefreshJWTStrategy:
    return RefreshJWTStrategy(
        secret=api_settings.SECRET_KEY,
        lifetime_seconds=jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS,
    )


bearer_transport = RefreshableBearerTransport(tokenUrl="auth/jwt/login")


authentication_backend = RefreshableAuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_access_strategy=get_access_jwt_strategy,
    get_refresh_strategy=get_refresh_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager, [authentication_backend]
)

UserManager = Annotated[_UserManager, Depends(get_user_manager)]
OAuth2Credentials = Annotated[OAuth2PasswordRequestForm, Depends()]

AccessStrategy = Annotated[
    AccessJWTStrategy, Depends(authentication_backend.get_strategy)
]

RefreshStrategy = Annotated[
    RefreshJWTStrategy, Depends(authentication_backend.get_refresh_strategy)
]

current_active_user_token = fastapi_users.authenticator.current_user_token(
    active=True
)

current_active_user = fastapi_users.current_user(active=True)


CurrentUserToken = Annotated[tuple, Depends(current_active_user_token)]
CurrentUser = Annotated[User, Depends(current_active_user)]


async def get_current_active_user_by_refresh_token(
    token: RefreshTokenSchema,
    strategy: RefreshStrategy,
    user_manager: UserManager,
) -> User:
    not_authorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = await strategy.read_token(token.refresh_token, user_manager)
    except exceptions.UserNotExists as e:
        raise not_authorized from e

    if not user:
        raise not_authorized

    if not user.is_active:
        raise not_authorized

    return user


CurrentUserByRefreshToken = Annotated[
    User, Depends(get_current_active_user_by_refresh_token)
]
