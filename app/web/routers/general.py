from fastapi import Depends, Request, APIRouter

from app.store.database.queries.users import UserDB
from app.web.dependencies import get_current_user
from app.web.exceptions.app_exceptions import (
    NotAuthenticatedException)
from app.config import templates
from app.store.database.queries.rooms import RoomDB

router = APIRouter()


@router.get("/", name='index')
async def index(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        raise NotAuthenticatedException(status_code=401)
    
    count_rooms = await RoomDB.count_rooms()
    count_users = await UserDB.count_users()
    contex = {'request': request,
              "count_rooms": count_rooms,
              "count_users": count_users,
              }
    return templates.TemplateResponse(
        'index.html', context=contex)
