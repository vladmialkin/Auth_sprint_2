from typing import Any, Dict
from clients.base.client import BaseClient
from django.conf import settings
import requests  # не забывайте импортировать requests для HTTP запросов


class AuthClient(BaseClient):
    def check_token(self, token: str) -> Dict[str, Any]:
        try:
            return self._post(
                "/check",
                headers={"Authorization": f"Bearer {token}"},
            )
        except requests.RequestException as e:
            # Здесь вы можете обработать ошибку по своему усмотрению
            print(f"Error checking token: {e}")
            return {}

    def login(self, username: str, password: str) -> dict[str, Any]:
        try:
            response = self._post(
                "/login",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                }
            )
            return response
        except requests.RequestException as e:
            print(f"Error logging in user {username}: {e}")
            return {}


# Инициализация клиента
auth_client = AuthClient(base_url=f"{settings.AUTH_API_URL}/api/v1/auth/jwt")
