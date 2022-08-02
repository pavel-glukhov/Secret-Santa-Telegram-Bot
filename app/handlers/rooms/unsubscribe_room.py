from typing import Union

from aiogram import types
from aiogram.types import ParseMode

from app import room_db
from app.keyborads.common import create_common_keyboards


async def left_room(message: types.Message, room_number: Union[str, int]):
    user_id = message.chat.id
    await room_db().remove_member(user_id, room_number)
    keyboard = await create_common_keyboards(message)

    await message.edit_text(f'Вы вышли из комнаты *{room_number}*.',
                            parse_mode=ParseMode.MARKDOWN)

    await message.answer(
        'Вы можете вернуться в комнату в любое время,'
        ' для этого используйте старый номер комнаты.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )
