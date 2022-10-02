import logging

from aiogram import types

from app.database import room_db
from app.keyborads.common import generate_inline_keyboard

logger = logging.getLogger(__name__)


async def my_room(message: types.Message, room_number):
    room = await room_db().get_room(room_number)
    room_name = room.name
    user_id = message.chat.id

    keyboard_dict = {
        "Ваши желания 🎁": f"room_show-wish_{room_number}",
        "Выйти из комнаты 🚪": f"room_exit_{room_number}"
    }

    is_owner = await room_db().is_owner(user_id=user_id,
                                        room_number=room_number)
    if is_owner:
        keyboard_dict.update(
            {
                "Начать игру 🎲": f"room_start-game_{room_number}",
                "Список участников 👥": f"room_member-list_{room_number}",
                "Настройки ⚒": f"room_config_{room_number}"
            }
        )
    keyboard_dict.update(
        {
            "Вернуться назад ◀️": f"root_menu",
        }
    )

    keyboard_inline_ = generate_inline_keyboard(keyboard_dict)
    await message.edit_text(f"Управление комнатой {room_name} ({room_number})",
                            reply_markup=keyboard_inline_)


async def members_list(message: types.Message,
                       room_number: int) -> None:
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}"
        }
    )

    room = await room_db().get_room(room_number)
    members = await room.members
    member_str = ''

    for number, member in enumerate(members):
        member_str += f'{number}) @{member.username}\n'

    await message.edit_text(
        f'Список участников комнаты: {room.name} ({room_number}):\n\n'
        f'{member_str}',
        reply_markup=keyboard_inline
    )
