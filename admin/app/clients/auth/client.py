from typing import Any
from clients.base.client import BaseClient
from django.conf import settings


class AuthClient(BaseClient):
    def check_token(self, token: str) -> dict[str, Any]:
        return self._post(
            "/check",
            headers={"Authorization": f"Bearer {token}"},
        )


auth_client = AuthClient(base_url=f"{settings.AUTH_API_URL}/auth/jwt")
