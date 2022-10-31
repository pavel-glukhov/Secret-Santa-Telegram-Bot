import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.store.database import room_db
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.handlers.utils.common import get_room_number

logger = logging.getLogger(__name__)


# TODO добавить логирование
@dp.callback_query_handler(Text(startswith='room_exit'))
async def left_room(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    user_id = callback.message.chat.id
    await room_db().remove_member(user_id, room_number)
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    await callback.message.edit_text(f'Вы вышли из комнаты *{room_number}*.', )
    await callback.message.answer(
        'Вы можете вернуться в комнату в любое время,'
        ' для этого используйте старый номер комнаты.',
        reply_markup=keyboard_inline,
    )
