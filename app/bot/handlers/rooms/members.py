import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_member-list'))
async def members_list(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    keyboard_inline = generate_inline_keyboard(
        {
            'Вернуться назад ◀️': f'room_menu_{room_number}'
        }
    )
    room = await RoomRepo().get(room_number)
    members = await room.members
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
