import jwt
from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.exceptions import HTTPException
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.jwt import decode_jwt
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.router.oauth import (
    STATE_TOKEN_AUDIENCE,
    generate_state_token,
)
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2Token

from app.api.deps.fastapi_users import (
    AccessStrategy,
    RefreshStrategy,
    UserManager,
    authentication_backend,
)
from app.api.deps.google_oauth import google_oauth2_client
from app.api.deps.session import Session
from app.api.deps.user_agent import UserAgent
from app.api.v1.schemas.google_oauth import OAuth2AuthorizeResponse
from app.settings.api import settings as api_settings

router = APIRouter()
callback_route_name = "oauth.callback"
oauth2_authorize_callback = OAuth2AuthorizeCallback(
    google_oauth2_client, route_name=callback_route_name
)

state_secret = api_settings.SECRET_KEY


@router.get(
    "/{social}/authorize",
    response_model=OAuth2AuthorizeResponse,
)
async def authorize(
    request: Request, social: str, scopes: list[str] = Query(None)
) -> OAuth2AuthorizeResponse:
    authorize_redirect_url = str(request.url_for(callback_route_name))

    match social:
        case "google":
            state_data: dict[str, str] = {}
            state = generate_state_token(state_data, state_secret)
            authorization_url = (
                await google_oauth2_client.get_authorization_url(
                    authorize_redirect_url,
                    state,
                    scopes,
                )
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown social: {social}.",
            )

    return OAuth2AuthorizeResponse(authorization_url=authorization_url)


@router.get(
    "/callback",
    name=callback_route_name,
    description="The response varies based on the authentication backend used.",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        "INVALID_STATE_TOKEN": {
                            "summary": "Invalid state token.",
                            "value": None,
                        },
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "User is inactive.",
                            "value": {
                                "detail": ErrorCode.LOGIN_BAD_CREDENTIALS
                            },
                        },
                    }
                }
            },
        },
    },
)
async def callback(
    request: Request,
    session: Session,
    user_manager: UserManager,
    access_strategy: AccessStrategy,
    refresh_strategy: RefreshStrategy,
    user_agent: UserAgent,
    access_token_state: tuple[OAuth2Token, str] = Depends(
        oauth2_authorize_callback
    ),
):
    token, state = access_token_state
    account_id, account_email = await google_oauth2_client.get_id_email(
        token["access_token"]
    )

    if account_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_NOT_AVAILABLE_EMAIL,
        )

    try:
        decode_jwt(state, state_secret, [STATE_TOKEN_AUDIENCE])
    except jwt.DecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e

    try:
        user = await user_manager.oauth_callback(
            google_oauth2_client.name,
            token["access_token"],
            account_id,
            account_email,
            token.get("expires_at"),
            token.get("refresh_token"),
            request,
            associate_by_email=True,
            is_verified_by_default=False,
        )
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_USER_ALREADY_EXISTS,
        ) from e

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    # Authenticate
    response = await authentication_backend.login(
        access_strategy, refresh_strategy, user, session, user_agent
    )
    await user_manager.on_after_login(user, request, response)
    return response
