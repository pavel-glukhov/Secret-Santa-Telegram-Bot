import logging
from urllib.parse import quote, unquote

from fastapi import APIRouter, Depends, Form, Request
from starlette.datastructures import MutableHeaders
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from app.config import templates
from app.store.database.models import User
from app.store.database.queries.rooms import RoomDB
from app.store.database.queries.users import UserDB
from app.store.scheduler import operations as scheduler_operations
from app.web.dependencies import get_current_user
from app.web.permissions import (is_admin_is_room_own_or_member,
                                 is_admin,
                                 is_admin_is_room_own)
from app.web.schemes import RemoveMemberConfirmation

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/rooms", name='rooms')
async def index(request: Request,
                current_user: User = Depends(get_current_user),
                permissions=Depends(is_admin), ):
    context = {
        'request': request,
        'current_user': current_user,
        'rooms': await RoomDB.get_all_rooms()
    }
    
    return templates.TemplateResponse(
        'rooms/rooms.html', context=context)


@router.get("/room/{room_number}", name='room')
async def index(request: Request, room_number: int,
                current_user: User = Depends(get_current_user),
                permissions=Depends(is_admin_is_room_own_or_member)):
    room = await RoomDB.get(room_number)
    if not room:
        raise HTTPException(status_code=404)
   

    
    members = await RoomDB.get_list_members(room_number=room_number)
    room_toss_time = scheduler_operations.get_task(room.number)
    if room_toss_time:
        room_toss_time = room_toss_time.next_run_time
    context = {
        'request': request,
        'current_user': current_user,
        'room': room,
        'room_owner': await room.owner,
        'toss_time': room_toss_time,
        'users': members,
    }
    
    return templates.TemplateResponse(
        'rooms/room.html', context=context, status_code=200)


@router.get("/room/{room_number}/remove_member/", name='user_leave_confirm')
async def remove_member_conf(request: Request, room_number: int,
                             current_user: User = Depends(get_current_user),
                             params=Depends(RemoveMemberConfirmation),
                             permissions=Depends(
                                 is_admin_is_room_own)):
    """
    The confirmation Endpoint to remove members from the room.
    Permissions: Only the superuser and the owner of the room,
                 but the owners cannot remove themselves from the room
    """
    is_room_owner = await RoomDB.is_owner(room_number=room_number,
                                    user_id=params.dict().get('user_id'))
    if is_room_owner:
        raise HTTPException(status_code=403)
        
    user_id = params.dict().get('user_id')
    context = {
        'request': request,
        'current_user': current_user,
        'number': room_number,
        'user': await UserDB.get_user_or_none(user_id),
        'referer': quote(request.headers.get('referer'), safe=''),
    }
    
    return templates.TemplateResponse(
        'users/leave_confirmation.html', context=context, status_code=200)


@router.post("/room/remove_member/", name='leave_user')
async def remove_member(request: Request, user_id: int = Form(...),
                        room_number: int = Form(...),
                        referer: str = Form(...), confirm: bool = Form(...),
                        current_user: User = Depends(get_current_user),
                        ):
    """
    The endpoint to remove members from the room.
    Permissions: Only the superuser and the owner of the room,
                 but the owners cannot remove themselves from the room
    """
    
    is_room_owner = await RoomDB.is_owner(room_number=room_number,
                                          user_id=user_id)
    logger.info(f'-----------{is_room_owner}')
    if is_room_owner:
        raise HTTPException(status_code=403)
    logger.info(f'-----------{confirm}')
    if confirm:
        await RoomDB.remove_member(user_id, room_number)
    
    return RedirectResponse(url=unquote(referer), status_code=301)
