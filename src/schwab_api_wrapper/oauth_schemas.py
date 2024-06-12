from pydantic import BaseModel


class Token(BaseModel):
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str
    access_token: str
    id_token: str


class OAuthError(BaseModel):
    error: str
    error_description: str
