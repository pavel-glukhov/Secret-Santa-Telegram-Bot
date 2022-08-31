import re
from typing import Union

from aiogram import types
from aiogram.types import ParseMode

from app.database import room_db


async def my_room(message: types.Message):
    description = re.findall(r': .+', message.text)[0]
    room_number = re.findall(r'\d{6}', message.text)[0]
    user_id = message.chat.id
    keyboard_inline = types.InlineKeyboardMarkup()

    keyboard_list = [
        types.InlineKeyboardButton(
            text="Ваши желания 🎁",  # TODO Реализовать и переименовать в посмотреть пожелания
            callback_data=f"room_show-wish_{room_number}"
        ), types.InlineKeyboardButton(
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
                text="Список участников 👥",  # TODO Добавить пагинацию
                callback_data=f"room_member-list_{room_number}"
            ),
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
        ])

    for button in keyboard_list:
        keyboard_inline.add(button)

    await message.answer(f"Управление комнатой {description}",
                         reply_markup=keyboard_inline)


async def members_list(message: types.Message,
                       room_number: int) -> None:
    room = await room_db().get_room(room_number)
    members = await room.members
    member_str = ''

    for i, member in enumerate(members):
        member_str += f'{i}) @{member.username}\n'

    await message.edit_text(
        f'Список участников комнаты: {room.name} ({room_number}):\n\n'
        f'{member_str}',
        parse_mode=ParseMode.MARKDOWN,
    )
