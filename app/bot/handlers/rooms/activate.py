import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


# TODO НУЖНО ПРОВЕРИТЬ!
@router.callback_query(F.data.startswith('room_activate'))
async def members_list(callback: types.CallbackQuery,
                       session: Session,
                       app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.room_menu.main_buttons.return_to_room_menu: f"room_menu_{room_number}"}
    )
    await RoomRepo(session).update(room_number, closed_at=None, is_closed=False)
    
    message_text = app_text_msg.messages.rooms_menu.activate.activate_msg
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
