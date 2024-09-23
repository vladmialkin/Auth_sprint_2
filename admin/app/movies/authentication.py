from django.contrib.auth.backends import BaseBackend
from rest_framework import authentication
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from clients.auth.client import auth_client
import http

User = get_user_model()


class Authentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth:
            raise exceptions.AuthenticationFailed("Not authenticated")

        if len(auth) != 2:
            msg = "Invalid token header"
            raise exceptions.AuthenticationFailed(msg)

        if user_data := auth_client.check_token(auth[1]):
            if user_data["active"]:
                return user_data

        raise exceptions.AuthenticationFailed("Not authenticated")


class CustomAuthentication(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            response = auth_client.login(username, password)

            if 'access_token' not in response:
                return None

            data = auth_client.check_token(response['access_token'])

            if data.get('is_active'):
                try:
                    user = User.objects.get(email=data.get('email'))
                except User.DoesNotExist:
                    user = User.objects.create(
                        id=data.get('id'),
                        email=data.get('email'),
                        is_active=data.get('is_active', True),
                        is_superuser=data.get('is_superuser', False),
                        is_verified=data.get('is_verified', False),
                    )
                return user
            return None

        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
