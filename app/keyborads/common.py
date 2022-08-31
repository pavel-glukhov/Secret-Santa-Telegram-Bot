from aiogram import types

from app.database import room_db
from app.keyborads.constants import MAIN_REPLY_BUTTONS


def personal_room_keyboard_form(room):
    return f'Ваша комната: {room.name} ({room.number})'


async def create_common_keyboards(message) -> types.ReplyKeyboardMarkup:
    user_id = message.chat.id
    rooms = await room_db().get_joined_in_rooms(user_id)
    users_list_rooms = []
    if rooms:
        for room in rooms:
            users_list_rooms.append(
                personal_room_keyboard_form(room)
            )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_room = types.KeyboardButton(text=MAIN_REPLY_BUTTONS['create_room'])
    join_room = types.KeyboardButton(text=MAIN_REPLY_BUTTONS['join_room'])
    about = types.KeyboardButton(text=MAIN_REPLY_BUTTONS['about'])
    user_profile = types.KeyboardButton(text=MAIN_REPLY_BUTTONS['user_profile'])

    keyboard.add(join_room, create_room)
    if users_list_rooms:
        for room in users_list_rooms:
            keyboard.add(room)
    keyboard.add(user_profile)
    keyboard.add(about)
    return keyboard
