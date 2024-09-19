from pydantic import BaseModel


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str
