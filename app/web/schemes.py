from pydantic import BaseModel

from app.config import load_config


class AuthJWTSettings(BaseModel):
    authjwt_secret_key: str = load_config().web.jwt_settings.authjwt_secret_key
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_secure: bool = True
    authjwt_cookie_csrf_protect: bool = False
    authjwt_cookie_samesite: str = 'none'
    authjwt_access_token_expires: bool = False
    authjwt_refresh_token_expires: bool = False


class RemoveMemberConfirmation(BaseModel):
    user_id: int
