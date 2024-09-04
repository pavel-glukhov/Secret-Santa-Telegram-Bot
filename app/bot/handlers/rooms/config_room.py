import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_config'))
async def configuration_room(callback: types.CallbackQuery, session: Session):
    room_number = get_room_number(callback)
    keyboard_inline = generate_inline_keyboard(
        {
            "Изменить имя комнаты ⚒": f"room_change-name_{room_number}",
            "Изменить бюджет 💶": f"room_change-budget_{room_number}",
            "Изменить владельца 👤": f"room_change-owner_{room_number}",
            "Удалить комнату ❌": f"room_delete_{room_number}",
            "Вернуться назад ◀️": f"room_menu_{room_number}",
        }
    )
    room = await RoomRepo(session).get(room_number)
    
    message_text = (
        '"Настройки комнаты:" '
        f' <b>{room.name}</b> (<b>{room_number}</b>)'
    )
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline, )
