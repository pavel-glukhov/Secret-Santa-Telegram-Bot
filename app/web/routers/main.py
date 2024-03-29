import logging

from fastapi import APIRouter, Depends, Request
from starlette.templating import Jinja2Templates

from app.store.database.models import User
from app.web.dependencies import get_current_user
from app.web.templates import template

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", name='index')
async def index(request: Request,
                current_user: User = Depends(get_current_user),
                templates: Jinja2Templates = Depends(template)):
    rooms = await current_user.members
    contex = {
        'request': request,
        'current_user': current_user,
        'rooms': rooms
    }
    return templates.TemplateResponse(
        'index.html', context=contex)
