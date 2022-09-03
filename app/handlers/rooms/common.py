import re
from typing import Union

from aiogram import types
from aiogram.types import ParseMode

from app.database import room_db


async def my_room(message: types.Message, room_number):
    room = await room_db().get_room(room_number)
    room_name = room.name
    user_id = message.chat.id

    keyboard_inline = types.InlineKeyboardMarkup()

    keyboard_list = [
        types.InlineKeyboardButton(
            text="Ваши желания 🎁",
            callback_data=f"room_show-wish_{room_number}"
        ),
        types.InlineKeyboardButton(
            text="Выйти из комнаты 🚪",
            callback_data=f"room_exit_{room_number}"
        ),
    ]

    is_owner = await room_db().is_owner(user_id=user_id,
                                        room_number=room_number)
    if is_owner:
        keyboard_list.extend([
            types.InlineKeyboardButton(
                text="Начать игру 🎲",  # TODO реализовать
                callback_data=f"room_member-list_{room_number}"
            ),
            types.InlineKeyboardButton(
                text="Список участников 👥",
                callback_data=f"room_member-list_{room_number}"
            ),
            types.InlineKeyboardButton(
                text="Настройки ⚒",
                callback_data=f"room_config_{room_number}"
            ),
        ])
    keyboard_list.extend([
        types.InlineKeyboardButton(
            text="Вернуться назад ◀️",
            callback_data=f"root_menu"
        )
    ])
    for button in keyboard_list:
        keyboard_inline.add(button)

    await message.edit_text(f"Управление комнатой {room_name} ({room_number})",
                            reply_markup=keyboard_inline)


async def members_list(message: types.Message,
                       room_number: int) -> None:
    keyboard_inline = types.InlineKeyboardMarkup()
    return_menu = types.InlineKeyboardButton(

        text="Вернуться назад ◀️",
        callback_data=f"room_menu_{room_number}"
    )

    room = await room_db().get_room(room_number)
    members = await room.members
    member_str = ''

    for i, member in enumerate(members):
        member_str += f'{i}) @{member.username}\n'

    keyboard_inline.add(return_menu)
    await message.edit_text(
        f'Список участников комнаты: {room.name} ({room_number}):\n\n'
        f'{member_str}',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )
