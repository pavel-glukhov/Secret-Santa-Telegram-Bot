import logging
from urllib.parse import quote, unquote

from fastapi import APIRouter, Depends, Form, Request
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.store.queries.pagination import PaginatorRepo
from app.web.templates import template
from app.store.database.models import User
from app.store.queries.rooms import RoomRepo
from app.store.queries.users import UserRepo
from app.web.dependencies import get_current_user
from app.web.permissions import is_admin, is_admin_or_owner

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/profile/{user_id}", name='profile')
async def profile(request: Request, user_id: int,
                  current_user: User = Depends(get_current_user),
                  templates: Jinja2Templates = Depends(template),
                  permissions=Depends(is_admin_or_owner)):
    """The endpoint provided information about selected user."""
    user_repo = UserRepo()
    room_repo = RoomRepo()
    user = await user_repo.get_user_or_none(user_id)
    rooms = await room_repo.get_all_users_of_room(user_id)
    
    if not user:
        raise HTTPException(status_code=404)
    context = {
        'request': request,
        'current_user': current_user,
        'user': user,
        'rooms': rooms,
    }
    
    return templates.TemplateResponse(
        'users/profile.html', context=context
    )


@router.get("/users", name='users')
async def users(request: Request, page: int = 1, limit: int = 10,
                current_user: User = Depends(get_current_user),
                templates: Jinja2Templates = Depends(template),
                permissions=Depends(is_admin)):
    """The endpoint provided list all users."""
    pagination_repo = PaginatorRepo()
    users, total_users = await pagination_repo.paginate(User, page, limit)
    context = {
        'request': request,
        'current_user': current_user,
        'users': users,
        'total_users': total_users,
        "page": page,
        "limit": limit
    }
    return templates.TemplateResponse(
        'users/users.html', context=context
    )


@router.post("/user/activate/{user_id}", name='activate_user')
async def activate(request: Request, user_id: int,
                   current_user: User = Depends(get_current_user),
                   templates: Jinja2Templates = Depends(template),
                   permissions=Depends(is_admin)):
    """
    The endpoint to activate or deactivate user's account.
    """
    user_repo = UserRepo()
    user = await user_repo.get_user_or_none(user=user_id)
    referer = request.headers.get('referer')
    
    if not user:
        raise HTTPException(status_code=404)
    
    if user.is_active:
        await user_repo.disable_user(user_id)
    else:
        await user_repo.enable_user(user_id)
    
    return RedirectResponse(url=referer, status_code=301)


@router.get("/user/{user_id}/delete_confirmation/", name='usr_del_confirmation')
async def index(request: Request, user_id: int,
                current_user: User = Depends(get_current_user),
                templates: Jinja2Templates = Depends(template),
                permissions=Depends(is_admin)):
    """The endpoint conformation that user can be deleted from DB."""
    
    referer = quote(request.headers.get('referer'), safe='')
    user_repo = UserRepo()
    user = await user_repo.get_user_or_none(user_id),
    
    context = {
        'request': request,
        'current_user': current_user,
        "user": user,
        'referer': referer,
    }
    
    return templates.TemplateResponse(
        'users//delete_confirmation.html', context=context)


@router.post("/user/delete/", name='delete_user')
async def delete(request: Request, user_id: int = Form(...),
                 referer: str = Form(...), confirm: bool = Form(...),
                 current_user: User = Depends(get_current_user),
                 templates: Jinja2Templates = Depends(template),
                 permissions=Depends(is_admin)):
    """The endpoint for deleting user from DB."""
    user_repo = UserRepo()
    if confirm:
        await user_repo.delete_user(user_id)
    
    return RedirectResponse(url=unquote(referer), status_code=301)
