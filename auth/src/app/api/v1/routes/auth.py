from fastapi import APIRouter, HTTPException, Response, status
from fastapi_users.router.common import ErrorCode

from app.api.deps.fastapi_users import (
    AccessStrategy,
    CurrentUserByRefreshToken,
    CurrentUserToken,
    OAuth2Credentials,
    RefreshStrategy,
    Session,
    UserManager,
    authentication_backend,
    fastapi_users,
)
from app.api.deps.user_agent import UserAgent
from app.api.v1.schemas.user import UserCreateSchema, UserRetrieveSchema
from app.users.schemas import BearerResponseSchema, RefreshResponseSchema

router = APIRouter()


@router.post("/login")
async def login(
    user_agent: UserAgent,
    user_manager: UserManager,
    access_strategy: AccessStrategy,
    refresh_strategy: RefreshStrategy,
    session: Session,
    credentials: OAuth2Credentials,
) -> BearerResponseSchema:
    """Вход пользователя в аккаунт."""
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    return await authentication_backend.login(
        access_strategy, refresh_strategy, user, session, user_agent
    )


@router.post("/logout")
async def logout(
    user_token: CurrentUserToken,
    user_agent: UserAgent,
    access_strategy: AccessStrategy,
    refresh_strategy: RefreshStrategy,
    session: Session,
) -> Response:
    """Выход пользователя из аккаунта."""
    user, token = user_token
    return await authentication_backend.logout(
        access_strategy,
        refresh_strategy,
        session,
        token,
        user,
        user_agent,
    )


@router.post("/refresh")
async def refresh(
    user: CurrentUserByRefreshToken,
    user_agent: UserAgent,
    access_strategy: AccessStrategy,
    refresh_strategy: RefreshStrategy,
    session: Session,
) -> RefreshResponseSchema:
    """Продление сессии пользователя."""
    return await authentication_backend.refresh(
        access_strategy, refresh_strategy, user, session, user_agent
    )


router.include_router(
    fastapi_users.get_register_router(UserRetrieveSchema, UserCreateSchema),
)
