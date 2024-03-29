import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_activate'))
async def members_list(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    keyboard_inline = generate_inline_keyboard(
        {'Вернуться в меню комнаты': f"room_menu_{room_number}"}
    )
    await RoomRepo().update(room_number, closed_at=None, is_closed=False)
    
    message_text = 'Комната повторно активирована.'
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
