from rest_framework import authentication
from rest_framework import exceptions
from clients.auth.client import auth_client


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

