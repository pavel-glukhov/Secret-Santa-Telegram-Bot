from typing import Optional

from pydantic import BaseModel
from app.config import load_config


class TelegramAuth(BaseModel):
    id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    photo_url: Optional[str]
    auth_date: Optional[str]
    hash: Optional[str]


class AuthJWTSettings(BaseModel):
    authjwt_secret_key: str = load_config().web.jwt_settings.authjwt_secret_key
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_secure: bool = False
    authjwt_cookie_csrf_protect: bool = True
    authjwt_cookie_samesite: str = 'none'
