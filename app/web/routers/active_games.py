import logging

from fastapi import APIRouter, Depends, Request

from app.config import templates
from app.store.database.models import User
from app.store.scheduler import operations as scheduler_operations
from app.web.dependencies import get_current_user
from app.web.permissions import is_admin

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/active_games", name='active_games')
async def active_games(request: Request,
                       current_user: User = Depends(get_current_user),
                       permissions=Depends(is_admin)):
    """The endpoint provided list all active scheduler tasks from Redis."""
    
    context = {
        'request': request,
        'current_user': current_user,
        'tasks': scheduler_operations.get_all_task(),
    }
    
    return templates.TemplateResponse(
        'games/active_games.html', context=context, status_code=200)
