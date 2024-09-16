import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session
from app.bot.languages import TranslationMainSchema

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_config'))
async def configuration_room(callback: types.CallbackQuery, session: Session, app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.room_menu.config_menu.room_change_name: f"room_change-name_{room_number}",
            app_text_msg.buttons.room_menu.config_menu.room_change_budget: f"room_change-budget_{room_number}",
            app_text_msg.buttons.room_menu.config_menu.room_change_owner: f"room_change-owner_{room_number}",
            app_text_msg.buttons.room_menu.config_menu.room_delete: f"room_delete_{room_number}",
            app_text_msg.buttons.return_back_button: f"room_menu_{room_number}",
        }
    )
    room = await RoomRepo(session).get(room_number)

    message_text = app_text_msg.messages.rooms_menu.config_room.main_menu.format(
        room_name=room.name,
        room_number=room_number
    )

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline, )
