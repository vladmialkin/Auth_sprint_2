from pydantic import BaseModel


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class BearerResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshResponseSchema(BaseModel):
    access_token: str
