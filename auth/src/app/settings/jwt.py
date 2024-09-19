from app.settings.base import Settings


class JWTSettings(Settings):
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 30 * 60  # 30 minutes
    REFRESH_TOKEN_LIFETIME_SECONDS: int = 60 * 60 * 24 * 7  # 7 days


settings = JWTSettings()
