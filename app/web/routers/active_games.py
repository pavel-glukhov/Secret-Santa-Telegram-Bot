import logging
from fastapi import APIRouter, Depends, Request

from app.store.scheduler import operations as scheduler_operations
from app.store.database.models import User
from app.store.database.queries.rooms import RoomDB
from app.web.dependencies import get_current_user

from app.config import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/active_games", name='active_games')
async def active_games(request: Request,
                       current_user: User = Depends(get_current_user)):
    # TODO add permissions [superuser]
    
    tasks = scheduler_operations.get_all_task()
    context = {
        'request': request,
        'current_user': current_user,
        'tasks': tasks,
    }
    
    return templates.TemplateResponse(
        'active_games.html', context=context, status_code=200)