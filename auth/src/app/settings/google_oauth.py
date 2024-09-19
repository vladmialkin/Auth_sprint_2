from app.settings.base import Settings


class GoogleOAuthSettings(Settings):
    GOOGLE_OAUTH_CLIENT_ID: str
    GOOGLE_OAUTH_CLIENT_SECRET: str


settings = GoogleOAuthSettings()
