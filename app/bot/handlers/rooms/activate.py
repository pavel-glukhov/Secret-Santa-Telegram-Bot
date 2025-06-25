import logging

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.core.database.repo.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_activate'))
async def members_list(callback: types.CallbackQuery,
                       session: AsyncSession,
                       lang: TranslationMainSchema,
                       room_number: int):
    return_to_room_menu_button = lang.buttons.room_menu.main_buttons.return_to_room_menu
    keyboard_inline = generate_inline_keyboard(
        {
            return_to_room_menu_button: f"room_menu_{room_number}"
        }
    )
    await RoomRepo(session).update(room_number, closed_at=None, is_closed=False)

    message_text = lang.messages.rooms_menu.activate.activate_msg

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
