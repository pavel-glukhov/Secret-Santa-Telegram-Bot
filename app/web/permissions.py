import logging

from fastapi import Depends
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.store.database.models import User
from app.store.database.queries.rooms import RoomDB
from app.web.dependencies import get_current_user

logger = logging.getLogger(__name__)

async def is_admin_is_room_own_or_member(request: Request, room_number: int=None,
                                 current_user: User = Depends(get_current_user)):
    
    if room_number is None:
        room_number = dict(await request.form()).get('room_number')
        
    room = await RoomDB.get(room_number)
    room_owner = await room.owner
    is_room_member = await RoomDB.is_member(room_number=room_number,
                                 user_id=current_user.user_id)
    
    if (current_user.is_superuser or
            room_owner.username == current_user.username or
            is_room_member):
        return True
    raise HTTPException(status_code=403)


async def is_admin_is_room_own(room_number: int,
                                         user: User = Depends(
                                             get_current_user)):
    room = await RoomDB.get(room_number)
    room_owner = await room.owner
    if (user.is_superuser or
            room_owner.username == user.username):
        return True
    raise HTTPException(status_code=403)

async def is_admin_or_owner(user_id: int,
                            user: User = Depends(get_current_user)):
    if user.is_superuser or user.user_id == user_id:
        return True
    raise HTTPException(status_code=403)


async def is_admin(user: User = Depends(get_current_user)):
    if user.is_superuser:
        return True
    raise HTTPException(status_code=403)
