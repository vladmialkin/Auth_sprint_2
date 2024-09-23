from typing import Annotated
import jwt
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from httpx.exceptions import ConnectError

from ..db.elastic import get_elastic
from ..db.redis import get_redis
from ..clients.auth.client import auth_client
from ..clients.auth.schemas import UserRetrieveSchema
from ..core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def decode_jwt(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET,
            settings.AUDIENCE,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
    return decoded_token


async def check_user(token: str = Depends(oauth2_scheme)) -> UserRetrieveSchema:
    try:
        return await auth_client.check(token)
    except Exception:
        data = decode_jwt(
            token,
            settings.SECRET,
            settings.AUDIENCE,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if not data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return UserRetrieveSchema(**data)


RedisConnection = Annotated[Redis, Depends(get_redis)]
ESConnection = Annotated[Redis, Depends(get_elastic)]
UserData = Annotated[UserRetrieveSchema, Depends(check_user)]

