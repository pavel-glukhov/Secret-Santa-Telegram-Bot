from aiogram import types
from aiogram.dispatcher.filters import Text

from app import dispatcher as dp
from app.database import room_db
from app.keyborads.common import generate_inline_keyboard


@dp.callback_query_handler(Text(startswith='room_config'))
async def configuration_room(callback: types.CallbackQuery):
    command, operation, room_number = callback.data.split('_')
    message = callback.message
    keyboard_inline = generate_inline_keyboard(
        {
            "Изменить имя комнаты ⚒": f"room_change-name_{room_number}",
            "Изменить владельца 👤": f"room_change-owner_{room_number}",
            "Удалить комнату ❌": f"room_delete_{room_number}",
            "Вернуться назад ◀️": f"room_menu_{room_number}",
        }
    )
    room = await room_db().get_room(room_number)
    room_name = room.name

    await message.edit_text("Настройки комнаты: "
                            f"*{room_name}* (*{room_number}*)",
                            reply_markup=keyboard_inline, )
