from fastapi import APIRouter, Depends, Request
from starlette.responses import HTMLResponse
from app.store.database.queries.rooms import RoomDB
from app.web.dependencies import get_current_user
from app.web.exceptions.app_exceptions import (
    NotAccessException,
    NotAuthenticatedException
)
from app.config import templates

router = APIRouter()


@router.get("/rooms", name='rooms')
async def index(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        raise NotAuthenticatedException(status_code=401)
    
    rooms = await RoomDB.get_all_rooms()
    
    context = {
        'request': request,
        'rooms': rooms
    }
    
    return templates.TemplateResponse(
        'rooms.html', context=context)


@router.get("/active_games", name='active_games')
async def index(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        raise NotAuthenticatedException(status_code=401)
    
    context = {
        'request': request,
        'id': current_user,
        'username': request.cookies.get('username'),
        'first_name': request.cookies.get('first_name'),
        'last_name': request.cookies.get('last_name'),
    }
    
    return templates.TemplateResponse(
        'active_games.html', context=context)
