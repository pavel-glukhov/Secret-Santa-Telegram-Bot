import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.store.database.repo.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_config'))
async def configuration_room(callback: types.CallbackQuery,
                             session: Session,
                             lang: TranslationMainSchema,
                             room_number: int):

    room_change_name_button = lang.buttons.room_menu.config_menu.room_change_name
    room_change_budget_button = lang.buttons.room_menu.config_menu.room_change_budget
    room_change_owner_button = lang.buttons.room_menu.config_menu.room_change_owner
    room_delete_button = lang.buttons.room_menu.config_menu.room_delete
    return_back_button_button = lang.buttons.return_back_button

    keyboard_inline = generate_inline_keyboard(
        {
            room_change_name_button: f"room_change-name_{room_number}",
            room_change_budget_button: f"room_change-budget_{room_number}",
            room_change_owner_button: f"room_change-owner_{room_number}",
            room_delete_button: f"room_delete_{room_number}",
            return_back_button_button: f"room_menu_{room_number}",
        }
    )
    room = await RoomRepo(session).get(room_number)

    message_text = lang.messages.rooms_menu.settings_menu.main_menu.format(
        room_name=room.name,
        room_number=room_number
    )

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
