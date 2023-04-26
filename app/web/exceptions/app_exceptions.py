from fastapi import HTTPException, Request, APIRouter
from starlette.responses import RedirectResponse

from app.config import templates

router = APIRouter()
class NotAuthenticatedException(HTTPException):
    pass


class NotAccessException(HTTPException):
    pass


class PageNotFoundException(HTTPException):
    pass


class InternalErrorException(HTTPException):
    pass


async def not_authenticated(request: Request, exc: HTTPException):
    return RedirectResponse(url='/login', status_code=301)


async def access_denied(request: Request, exc: HTTPException):
    return templates.TemplateResponse('errors/403.html', {'request': request},
                                      status_code=403)


async def not_found_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse('errors/404.html', {'request': request},
                                      status_code=404)


async def internal_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse('errors/500.html', {'request': request},
                                      status_code=500)
