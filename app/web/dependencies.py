import logging

from fastapi import Depends, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqlalchemy.orm import scoped_session
from starlette.exceptions import HTTPException

from app.store.database.models import User
from app.store.database.queries.users import UserRepo
from app.store.database.sessions import get_session

logger = logging.getLogger(__name__)


async def get_current_user(request: Request,
                           Authorize: AuthJWT = Depends(),
                           session: scoped_session = Depends(get_session)) -> User | None:
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = await UserRepo(session).get_user_or_none(current_user)
        if user:
            return user
        return None
    except AuthJWTException as exc:
        logger.error(f'get_current_user: {exc.message}')
        raise HTTPException(status_code=401)
