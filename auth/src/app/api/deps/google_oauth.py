from httpx_oauth.clients.google import GoogleOAuth2

from app.settings.google_oauth import settings as google_oauth_settings

google_oauth2_client = GoogleOAuth2(
    google_oauth_settings.GOOGLE_OAUTH_CLIENT_ID,
    google_oauth_settings.GOOGLE_OAUTH_CLIENT_SECRET,
)
