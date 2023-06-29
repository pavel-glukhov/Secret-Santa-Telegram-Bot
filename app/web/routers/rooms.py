import logging
from urllib.parse import quote, unquote

from fastapi import APIRouter, Depends, Request, Form
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from app.store.database.models import User
from app.store.database.queries.rooms import RoomDB
from app.store.database.queries.users import UserDB
from app.web.dependencies import get_current_user

from app.config import templates
from app.web.schemes import RemoveMemberConfirmation

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/rooms", name='rooms')
async def index(request: Request,
                current_user: User = Depends(get_current_user)):
    # TODO add permissions
    # only superuser
    rooms = await RoomDB.get_all_rooms()
    
    context = {
        'request': request,
        'current_user': current_user,
        'rooms': rooms
    }
    
    return templates.TemplateResponse(
        'rooms//rooms.html', context=context)


@router.get("/room/{room_number}", name='room')
async def index(request: Request, room_number: int,
                current_user: User = Depends(get_current_user),
                ):
    # TODO add permissions
    room = await RoomDB.get(room_number)
    if not room:
        raise HTTPException(status_code=404)
    members = await RoomDB.get_list_members(room_number=room_number)
    
    context = {
        'request': request,
        'current_user': current_user,
        'room': room,
        'room_owner': await room.owner,
        'users': members,
        
    }

    return templates.TemplateResponse(
        'rooms/room.html', context=context, status_code=200)


@router.get("/active_games", name='active_games')
async def active_games(request: Request,
                current_user: User = Depends(get_current_user)):
    # TODO add permissions
    # only superuser
    context = {
        'request': request,
        'current_user': current_user,
        'username': request.cookies.get('username'),
        'first_name': request.cookies.get('first_name'),
        'last_name': request.cookies.get('last_name'),
    }
    
    return templates.TemplateResponse(
        'active_games.html', context=context, status_code=200)


# # TODO
@router.get("/room/{room_number}/remove_member/", name='user_leave_confirm')
async def remove_member_conf(request: Request, room_number: int,
                current_user: User = Depends(get_current_user),
                params = Depends(RemoveMemberConfirmation)
                ):
    
    # TODO add permissions
    # only superuser or owner
    
    user_id = params.dict().get('user_id')
    context = {
        'request': request,
        'current_user': current_user,
        'number': room_number,
        'user': await UserDB.get_user_or_none(user_id),
        'referer': quote(request.headers.get('referer'), safe='')
        
    }
    return templates.TemplateResponse(
        'users/leave_confirmation.html', context=context, status_code=200)


# # TODO
@router.post("/room/remove_member/", name='leave_user')
async def remove_member(request: Request, user_id: int = Form(...),
                room_number: int = Form(...),
                referer: str = Form(...), confirm: bool = Form(...),
                current_user: User = Depends(get_current_user)):
    # TODO add permissions
    # only superuser or owner
    if confirm:
        await RoomDB.remove_member(user_id, room_number)
    
    return RedirectResponse(url=unquote(referer), status_code=301)