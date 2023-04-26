from fastapi import Depends, Request, APIRouter

from app.web.dependencies import get_current_user
from app.web.exceptions.app_exceptions import (
    NotAuthenticatedException)
from app.config import templates

router = APIRouter()


@router.get("/", name='index')
def index(request: Request, current_user=Depends(get_current_user)):
    if current_user:
        return templates.TemplateResponse(
            'index.html', {'request': request, })
    
    raise NotAuthenticatedException(status_code=401)
