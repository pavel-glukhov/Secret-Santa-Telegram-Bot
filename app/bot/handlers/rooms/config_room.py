from aiogram import types
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.rooms import RoomRepo


@dp.callback_query_handler(Text(startswith='room_config'))
async def configuration_room(callback: types.CallbackQuery):
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
    room = await RoomRepo().get(room_number)

    message_text = (
        '"Настройки комнаты:" '
        f' <b>{room.name}</b> (<b>{room_number}</b>)'
    )
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline, )
