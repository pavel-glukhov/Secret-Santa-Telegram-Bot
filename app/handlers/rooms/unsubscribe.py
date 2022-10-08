import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import Text

from app import dispatcher as dp
from app.database import room_db
from app.keyborads.common import generate_inline_keyboard

logger = logging.getLogger(__name__)


# TODO добавить логирование
@dp.callback_query_handler(Text(startswith='room_exit'))
async def left_room(callback: types.CallbackQuery):
    command, operation, room_number = callback.data.split('_')
    message = callback.message
    user_id = message.chat.id
    await room_db().remove_member(user_id, room_number)
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )

    await message.edit_text(f'Вы вышли из комнаты *{room_number}*.', )

    await message.answer(
        'Вы можете вернуться в комнату в любое время,'
        ' для этого используйте старый номер комнаты.',
        reply_markup=keyboard_inline
    )
