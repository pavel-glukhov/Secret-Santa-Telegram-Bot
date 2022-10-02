from aiogram import types

from app.database import room_db
from app.keyborads.common import generate_inline_keyboard


async def configuration_room(message: types.Message, room_number):
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
