from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from app.bot.languages.schemes import TranslationMainSchema
from app.config import load_config
from app.store.database.models import Room
from app.store.database.queries.rooms import RoomRepo
from app.store.scheduler.operations import TaskScheduler


async def create_common_keyboards(message: types.Message, session: Session,
                                  text: TranslationMainSchema) -> types.InlineKeyboardMarkup:
    """
    Generating main buttons
    :param message:
    :param session:
    :param text:
    :return:
    """
    # general buttons
    count_user_rooms = await RoomRepo(session).get_count_user_rooms(
        message.chat.id)
    keyboard_dict = {text.buttons.main_menu.join_room: "menu_join_room"}
    
    if count_user_rooms < load_config().room.user_rooms_count:
        keyboard_dict.update(
            {text.buttons.main_menu.create_room: "menu_create_new_room"}
        )
        
    user_id = message.chat.id
    user_rooms = await RoomRepo(session).get_all_users_of_room(user_id)

    if user_rooms:
        for room in user_rooms:
            owner = room.owner
            is_owner = owner.user_id == user_id
            # add all users rooms' buttons
            keyboard_dict.update(
                {
                    personal_room_keyboard_formatter(
                        room, is_owner, text.formatter.your_room
                    ): f"room_menu_{room.number}"
                }
            )
    # general buttons that mast be in end of buttons list
    keyboard_dict.update(
        {
            text.buttons.main_menu.user_profile: "menu_user_profile",
            text.buttons.main_menu.about: "menu_about_game",
        }
    )
    keyboard_inline = generate_inline_keyboard(keyboard_dict)

    return keyboard_inline


def personal_room_keyboard_formatter(
        room: Room, is_owner: bool, text_message: str) -> str:
    """
    Formatter for user's room button.
    Showing different message if user is owner of room.

    :param room:
    :param is_owner:
    :param text_message:
    :return:
    """
    owner_tag = ' 🤴' if is_owner else ''
    scheduler_tag = '⏱' if TaskScheduler().get_task(room.number) else ''
    closed_tag = '✅' if room.is_closed else ''
    
    return (f'{text_message}: {room.name} ({room.number})'
            f'{owner_tag} {scheduler_tag} {closed_tag}')


def generate_inline_keyboard(buttons: dict) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, val in buttons.items():
        button = types.InlineKeyboardButton(
            text=key,
            callback_data=val
        )
        builder.row(button)
    return builder.as_markup()
