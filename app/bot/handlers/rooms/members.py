import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith('room_member-list'))
async def members_list(callback: types.CallbackQuery, session: Session):
    room_number = get_room_number(callback)
    keyboard_inline = generate_inline_keyboard(
        {
            'Вернуться назад ◀️': f'room_menu_{room_number}'
        }
    )
    room = await RoomRepo(session).get(room_number)
    members = room.members
    member_string = ''
    for number, member in enumerate(members, start=1):
        if member.first_name:
            if member.username and member.last_name:
                user_name = (f'@{member.username} - '
                             f'{member.first_name} {member.last_name}')
            elif member.username and not member.last_name:
                user_name = f'@{member.username} - {member.first_name}'
            elif not member.username and member.last_name:
                user_name = f'{member.first_name} {member.last_name}'
            
            else:
                user_name = member.first_name
        else:
            user_name = None
        
        member_string += (
            f'{number}) {user_name}\n')
    
    message_text = (
        'Список участников комнаты: '
        f'<b>{room.name} ({room_number})</b>:\n\n{member_string}'
    )
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
