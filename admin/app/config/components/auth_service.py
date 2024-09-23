from config.components.base import env

AUTH_USER_MODEL = "movies.User"

AUTH_API_URL = env.str("AUTH_API_URL")

AUTHENTICATION_BACKENDS = [
    'movies.authentication.Authentication',
]
