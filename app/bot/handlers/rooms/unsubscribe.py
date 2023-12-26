import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_exit'))
async def left_room(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    user_id = callback.message.chat.id
    await RoomRepo().remove_member(user_id, room_number)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )

    message_text = f'Вы вышли из комнаты <b>{room_number}</b>.'
    
    await callback.message.edit_text(
        text=message_text,
    )

    message_text = (
        'Вы можете вернуться в комнату в любое время, '
        f'для этого используйте номер комнаты <b>{room_number}</b>.'
    )
    await callback.message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    logger.info(
        f'The user[{callback.message.from_user.id}]'
        f' left from the room[{room_number}]'
    )
