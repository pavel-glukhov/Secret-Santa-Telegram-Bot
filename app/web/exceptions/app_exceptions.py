from fastapi import Depends, Request
from starlette.responses import RedirectResponse

from app.config import templates
from app.store.database.models import User
from app.web.dependencies import get_current_user


# TODO переделать перенаправление на страницу login
async def not_authenticated(request: Request, exc):
    return RedirectResponse(url='/login', status_code=301)

async def access_denied(request: Request, exc,
                        current_user: User = Depends(get_current_user)):
    context = {
        'request': request,
        'current_user': current_user,
    }
    return templates.TemplateResponse('errors//403.html', context=context,
                                      status_code=403)


async def not_found_error(request: Request, exc,
                          current_user: User = Depends(get_current_user)):
    context = {
        'request': request,
        'current_user': current_user,
    }
    return templates.TemplateResponse('errors//404.html', context=context,
                                      status_code=404)


async def internal_error(request: Request, exc):
    return templates.TemplateResponse('errors//500.html', {'request': request},
                                      status_code=500)
