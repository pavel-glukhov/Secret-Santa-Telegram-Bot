import logging

from fastapi import Depends, Request, APIRouter
from app.store.database.models import User
from app.store.database.queries.users import UserDB
from app.web.dependencies import get_current_user
from app.config import templates
from app.store.database.queries.rooms import RoomDB

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", name='index')
async def index(request: Request,
                current_user: User = Depends(get_current_user)):
    
    rooms = await current_user.members
    contex = {
        'request': request,
        'current_user': current_user,
        'rooms': rooms

    }
    return templates.TemplateResponse(
        'index.html', context=contex)
