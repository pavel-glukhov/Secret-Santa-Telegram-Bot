from aiogram import types
from aiogram.types import ParseMode

from app.database import room_db


async def configuration_room(message: types.Message, room_number):
    keyboard_inline = types.InlineKeyboardMarkup()
    room = await room_db().get_room(room_number)
    room_name = room.name

    keyboard_list = [
        types.InlineKeyboardButton(
            text="Изменить имя комнаты ⚒",  #
            callback_data=f"room_change-name_{room_number}"
        ),
        types.InlineKeyboardButton(
            text="Изменить владельца 👤",
            callback_data=f"room_change-owner_{room_number}"
        ),
        types.InlineKeyboardButton(
            text="Удалить комнату ❌",
            callback_data=f"room_delete_{room_number}"
        ),
        types.InlineKeyboardButton(
            text="Вернуться назад ◀️",
            callback_data=f"room_menu_{room_number}"
        ),
    ]

    for button in keyboard_list:
        keyboard_inline.add(button)

    await message.edit_text("Настройки комнаты: "
                            f"*{room_name}* (*{room_number}*)",
                            reply_markup=keyboard_inline,
                            parse_mode=ParseMode.MARKDOWN)
