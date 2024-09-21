from src.clients.base.client import BaseClient
from src.clients.auth.schemas import UserRetrieveSchema
from src.core.config import settings


class AuthClient(BaseClient):
    async def check(self, token: str) -> UserRetrieveSchema:
        user = await self._post("/check", headers={"Authorization": f"Bearer {token}"})
        return UserRetrieveSchema.model_validate(user)


auth_client = AuthClient(
    base_url=f"{settings.AUTH_API_URL}/auth/jwt"
)