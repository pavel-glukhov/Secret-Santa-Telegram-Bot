from aiogram import types

from app.bot.keyborads.constants import MAIN_REPLY_BUTTONS
from app.config import load_config
from app.store.database.models import Room
from app.store.queries.rooms import RoomRepo
from app.store.scheduler.operations import get_task


def generate_inline_keyboard(buttons: dict) -> types.InlineKeyboardMarkup:
    keyboard_inline = types.InlineKeyboardMarkup()
    
    for key, val in buttons.items():
        button = types.InlineKeyboardButton(
            text=key,
            callback_data=val
        )
        keyboard_inline.add(button)
    
    return keyboard_inline


def personal_room_keyboard_formatter(room: Room, is_owner: bool) -> str:
    """
    Formatter for user's room button.
    Showing different message if user is owner of room.

    :param room:
    :param is_owner:
    :return:
    """
    owner_tag = ' 🤴' if is_owner else ''
    scheduler_tag = '⏱' if get_task(room.number) else ''
    closed_tag = '✅' if room.is_closed else ''
    text = 'Ваша комната'
    return (f'{text}: {room.name} ({room.number})'
            f'{owner_tag} {scheduler_tag}{closed_tag}')


async def create_common_keyboards(
        message: types.Message
) -> types.InlineKeyboardMarkup:
    """
    Generating main buttons
    :param message:
    :return:
    """
    # general buttons
    count_user_rooms = await RoomRepo().get_count_user_rooms(
        message.chat.id)
    keyboard_dict = {MAIN_REPLY_BUTTONS['join_room']: "menu_join_room"}
    if count_user_rooms < load_config().room.user_rooms_count:
        keyboard_dict.update(
            {MAIN_REPLY_BUTTONS['create_room']: "menu_create_new_room"}
        )
    user_id = message.chat.id
    user_rooms = await RoomRepo().get_all_users_of_room(user_id)
    
    if user_rooms:
        for room in user_rooms:
            owner = await room.owner
            is_owner = owner.user_id == user_id
            # add all users rooms' buttons
            keyboard_dict.update(
                {
                    personal_room_keyboard_formatter(
                        room, is_owner
                    ): f"room_menu_{room.number}"
                }
            )
    # general buttons that mast be in end of buttons list
    keyboard_dict.update(
        {
            MAIN_REPLY_BUTTONS['user_profile']: "menu_user_profile",
            MAIN_REPLY_BUTTONS['about']: "menu_about_game",
        }
    )
    keyboard_inline = generate_inline_keyboard(keyboard_dict)
    
    return keyboard_inline
