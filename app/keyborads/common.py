from aiogram import types

from app.database import room_db
from app.keyborads.constants import MAIN_REPLY_BUTTONS


def generate_inline_keyboard(buttons: dict) -> types.InlineKeyboardMarkup:
    keyboard_inline = types.InlineKeyboardMarkup()

    for key, val in buttons.items():
        button = types.InlineKeyboardButton(
            text=key,
            callback_data=val
        )
        keyboard_inline.add(button)

    return keyboard_inline


def personal_room_keyboard_form(room, is_owner):
    owner_tag = ' 🤴' if is_owner else ''
    text = 'Управление комнатой' if is_owner else 'Ваша комната'
    return f'{text}: {room.name} ({room.number}){owner_tag}'


async def create_common_keyboards(message):
    users_list_rooms = []
    keyboard_inline = types.InlineKeyboardMarkup()

    create_room = types.InlineKeyboardButton(
        text=MAIN_REPLY_BUTTONS['create_room'],
        callback_data=f"menu_create_new_room"
    )

    join_room = types.InlineKeyboardButton(
        text=MAIN_REPLY_BUTTONS['join_room'],
        callback_data=f"menu_join_room"
    )

    profile = types.InlineKeyboardButton(
        text=MAIN_REPLY_BUTTONS['user_profile'],
        callback_data=f"menu_user_profile"
    )

    about = types.InlineKeyboardButton(
        text=MAIN_REPLY_BUTTONS['about'],
        callback_data=f"menu_about_game")

    user_id = message.chat.id
    rooms = await room_db().get_all_user_rooms(user_id)

    if rooms:
        for room in rooms:
            owner = await room.owner
            is_owner = owner.user_id == user_id

            users_list_rooms.append(
                types.InlineKeyboardButton(
                    text=personal_room_keyboard_form(room, is_owner),
                    callback_data=f"room_menu_{room.number}")
            )

    # first line of buttons
    keyboard_inline.add(create_room, join_room)

    # list of user's rooms
    if users_list_rooms:
        for button in users_list_rooms:
            keyboard_inline.add(button)

    # profile and about list of buttons
    keyboard_inline.add(profile)
    keyboard_inline.add(about)

    return keyboard_inline
