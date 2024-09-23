from httpx_oauth.clients.google import GoogleOAuth2

from auth.src.app.settings.oauth import settings as oauth_settings

google_oauth2_client = GoogleOAuth2(
    oauth_settings.GOOGLE_OAUTH_CLIENT_ID,
    oauth_settings.GOOGLE_OAUTH_CLIENT_SECRET,
)
