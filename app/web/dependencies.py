import logging

from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.exceptions import HTTPException

from app.store.database.models import User
from app.store.database.queries.users import UserDB
from app.web.schemes import AuthJWTSettings


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()


logger = logging.getLogger(__name__)


async def get_current_user(Authorize: AuthJWT = Depends()):
    # TODO убрать заглушку при переводе на вебхуки
    # "---------------------------------------------------------------"
    try:
        # Заглушка#
        user_id = 245942576
        # current_user = Authorize.get_jwt_subject()
        # Authorize.jwt_required()
        user = await UserDB.get_user_or_none(user_id)
        if not user:
            raise HTTPException(status_code=401)
        return user
    except AuthJWTException:
        raise HTTPException(status_code=401)


async def is_admin_or_room_owner(room_number: int,
                                 user: User = Depends(get_current_user)):
    is_owner = await UserDB.is_room_owner(user, room_number)
    if user.is_superuser or is_owner:
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