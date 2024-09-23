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


# Улучшенный метод аутентификации
class CustomAuthentication(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            response = auth_client.login(username, password)

            if len(response) == 2:
                data = auth_client.check_token(response.get('access_token'))
                user, created = User.objects.get_or_create(id=data.get('id'))
                if created is False:
                    user.email = data.get('email')
                    user.is_active = data.get('is_active')
                    user.is_superuser = data.get('is_superuser')
                    user.is_verified = data.get('is_verified')
                    user.save()
                return user
            return None
        except Exception as e:
            print(f"Error occurred during authentication: {str(e)}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
