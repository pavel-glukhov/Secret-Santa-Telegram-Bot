from fastapi import APIRouter, Depends, Request
from starlette.responses import HTMLResponse

from app.web.dependencies import get_current_user
from app.web.exceptions.app_exceptions import NotAccessException
from app.config import templates

router = APIRouter()


@router.get("/profile", response_class=HTMLResponse)
def profile(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        raise NotAccessException(status_code=403)
    
    context = {
        'request': request,
        'id': current_user,
        'username': request.cookies.get('username'),
        'first_name': request.cookies.get('first_name'),
        'last_name': request.cookies.get('last_name'),
    }
    
    return templates.TemplateResponse(
        'profile.html', context=context
    )
