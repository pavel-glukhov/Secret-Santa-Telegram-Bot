import logging

from fastapi import Depends,Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.exceptions import HTTPException

from app.store.database.models import User
from app.store.queries.users import UserRepo


logger = logging.getLogger(__name__)


async def get_current_user(request: Request,
                           Authorize: AuthJWT = Depends()) -> User | None:
    user_repo = UserRepo()
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = await user_repo.get_user_or_none(current_user)
        if user:
            return user
        return None
    except AuthJWTException as exc:
        logger.error(f'get_current_user: {exc.message}')
        raise HTTPException(status_code=401)
