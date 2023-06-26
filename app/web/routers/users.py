from fastapi import APIRouter, Depends, Request
from starlette.responses import HTMLResponse

from app.store.database.queries.rooms import RoomDB
from app.store.database.queries.users import UserDB
from app.web.dependencies import get_current_user
from app.web.exceptions.app_exceptions import (
    NotAccessException,
    NotAuthenticatedException
)
from app.config import templates

router = APIRouter()


@router.get("/profile/{number}", name='profile')
async def profile(request: Request, number: int,
                  current_user=Depends(get_current_user)):
    if not current_user:
        raise NotAccessException(status_code=403)
    
    user = await UserDB.get_user_or_none(number)
    rooms = await RoomDB.get_all_users_of_room(number)

    context = {
        'request': request,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'telegram_id': user.user_id,
        'status': user.is_active,
        'is_superuser': user.is_superuser,
        'rooms':rooms,
    }

    
    return templates.TemplateResponse(
        'profile.html', context=context
    )


@router.get("/users", name='users')
async def index(request: Request, current_user=Depends(get_current_user)):
    if current_user:
        return templates.TemplateResponse(
            'users.html', {'request': request, })
    
    raise NotAuthenticatedException(status_code=401)
