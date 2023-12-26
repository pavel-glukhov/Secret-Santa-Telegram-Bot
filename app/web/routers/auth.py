import logging

from fastapi import APIRouter, Depends, Request
from fastapi_jwt_auth import AuthJWT
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.config import load_config, AppConfig
from app.web.templates import template
from app.store.queries.users import UserRepo
from app.web.auth_widget.exceptions import (TelegramDataError,
                                            TelegramDataIsOutdated)
from app.web.schemes import AuthJWTSettings
from app.web.auth_widget.schemes import TelegramAuth
from app.web.auth_widget.validators import validate_telegram_data
from app.web.auth_widget.widget import TelegramLoginWidget, Size

router = APIRouter()

logger = logging.getLogger(__name__)


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()


@router.get("/login", name='login')
async def login(request: Request,
                params: TelegramAuth = Depends(TelegramAuth),
                Authorize: AuthJWT = Depends(),
                config: AppConfig = Depends(load_config),
                       templates: Jinja2Templates = Depends(template)):
    """
    Endpoint for authorization via Telegram.
    If the user is already logged in, returns it to the main page.
    In the absence of authorization, checks for the presence of 'hash'
    in the request and renders the authorization page.
    When receiving the 'hash', redirects to an attempt to validate
    the received data. In case of success a token is issued.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    user_repo = UserRepo()
    redirect_response = RedirectResponse(url='/', status_code=307)
    
    if current_user:
        get_jwt_token({'id': current_user}, redirect_response, Authorize)
        return redirect_response
    
    if not params.dict().get('hash'):
        widget = TelegramLoginWidget(
            telegram_login=config.bot.telegram_login,
            size=Size.LARGE
        )
        
        redirect_widget = widget.redirect_telegram_login_widget(
            redirect_url=str(request.url_for('login')))
        
        return templates.TemplateResponse(
            'login.html', context={
                'request': request,
                'redirect_widget': redirect_widget,
                'current_user': current_user,
            }
        )
    
    try:
        result = validate_telegram_data(config.bot.token, params)
        if result:
            await user_repo.get_or_create(
                user_id=params.id,
                first_name=params.first_name,
                last_name=params.last_name,
                username=params.username,
            )
            
            get_jwt_token(result, redirect_response, Authorize)
            
            return redirect_response
        raise HTTPException(status_code=403)
    
    except TelegramDataIsOutdated:
        raise HTTPException(status_code=500)
    except TelegramDataError:
        raise HTTPException(status_code=500)


def get_jwt_token(params: dict, response: RedirectResponse,
                  Authorize: AuthJWT) -> None:
    access_token = Authorize.create_access_token(params['id'])
    refresh_token = Authorize.create_refresh_token(params['id'])
    Authorize.set_access_cookies(access_token, response)
    Authorize.set_refresh_cookies(refresh_token, response)


@router.delete('/logout', response_class=HTMLResponse)
def logout(request: Request, Authorize: AuthJWT = Depends()):
    """
    Because the JWT are stored in a httponly cookie now, we cannot
    log the user out by simply deleting the cookie in the frontend.
    We need the backend to send us a response to delete the cookies.
    """
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    Authorize.unset_access_cookies()
    Authorize.unset_refresh_cookies()
    raise HTTPException(status_code=401)
