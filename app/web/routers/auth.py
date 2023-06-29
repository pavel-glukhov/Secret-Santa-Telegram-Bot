from fastapi import APIRouter, Depends, Request
from fastapi_jwt_auth import AuthJWT
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.exceptions import HTTPException
from app.web.dependencies import get_current_user
from app.web.exceptions.telegram_exceptions import (TelegramDataError,
                                                TelegramDataIsOutdated)
from app.web.schemes import TelegramAuth, AuthJWTSettings
from app.config import load_config
from app.config import templates
from app.web.validators import verify_telegram_authentication

router = APIRouter()


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()


@router.get("/login", name='login')
async def login(request: Request,
          params: TelegramAuth = Depends(TelegramAuth),
          current_user=Depends(get_current_user),
          Authorize: AuthJWT = Depends()):
    """
    Endpoint for authorization via Telegram.
    If the user is already logged in, returns it to the main page.
    In the absence of authorization, checks for the presence of 'hash'
    in the request and renders the authorization page.
    When receiving the 'hash', redirects to an attempt to validate
    the received data. In case of success a token is issued.
    """
    app_config = load_config()
    redirect_response = RedirectResponse(url='/',
                                         status_code=307)
    

    if current_user:
        get_jwt_token({'id': current_user}, redirect_response, Authorize)
        return redirect_response
    
    if not params.dict().get('hash'):
        return templates.TemplateResponse(
            'login.html',
            {
                'request': request,
                'telegram_login': app_config.bot.telegram_login,
                'auth_url': app_config.bot.auth_url
            }
        )
    
    try:
        result = verify_telegram_authentication(
            app_config.bot.token, params.dict()
        )
        if result:

            get_jwt_token(result, redirect_response, Authorize)
            # TODO Проверка на существование пользователя в БД
            return redirect_response
        
        raise HTTPException(status_code=403)
    
    except TelegramDataIsOutdated:
        raise HTTPException(status_code=500)
    except TelegramDataError:
        raise HTTPException(status_code=500)


def get_jwt_token(params, response, Authorize):
    access_token = Authorize.create_access_token(
        subject=params['id'])
    
    refresh_token = Authorize.create_refresh_token(
        subject=params['id'])
    
    Authorize.set_access_cookies(access_token, response=response)
    Authorize.set_refresh_cookies(refresh_token, response=response)


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
