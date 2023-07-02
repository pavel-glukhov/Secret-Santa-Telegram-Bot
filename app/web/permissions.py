from fastapi import Depends
from starlette.exceptions import HTTPException

from app.store.database.models import User
from app.store.database.queries.rooms import RoomDB
from app.web.dependencies import get_current_user


async def is_admin_is_room_own_or_member(room_number: int,
                                 user: User = Depends(get_current_user)):
    room = await RoomDB.get(room_number)
    room_owner = await room.owner
    is_room_member = RoomDB.is_member(room_number=room_number,
                                 user_id=user.user_id)
    
    if (user.is_superuser or
            room_owner.username == user.username or
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
