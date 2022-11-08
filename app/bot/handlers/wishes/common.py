import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database import room_db, wish_db

logger = logging.getLogger(__name__)


class ChangeWish(StatesGroup):
    waiting_for_wishes = State()


@dp.callback_query_handler(Text(startswith='room_show-wish'))
async def show_wishes(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    message = callback.message
    keyboard_inline = generate_inline_keyboard(
        {
            "Изменить желание ✒️": f"room_change-wish_{room_number}",
            "Вернуться назад ◀️": f"room_menu_{room_number}",

        }
    )

    user_id = message.chat.id
    wishes = await wish_db().get(user_id, room_number)

    await message.edit_text('Ваши тайные желания 🙊: \n'
                            f'{wishes.wish}\n',
                            reply_markup=keyboard_inline)


@dp.callback_query_handler(Text(startswith='room_change-wish'))
async def update_wishes(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    message = callback.message
    await ChangeWish.waiting_for_wishes.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    await message.edit_text(
        '<b>Напиши новое желание:</b>\n',
    )


@dp.message_handler(state=ChangeWish.waiting_for_wishes)
async def process_updating_wishes(message: types.Message, state: FSMContext):
    state_data = await dp.current_state().get_data()
    room_number = state_data['room_number']
    wish = message.text
    user_id = message.chat.id

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}",
        }
    )
    await wish_db().update_or_create(
        wish,
        user_id,
        room_number
    )
    room = await room_db().get(room_number)
    await state.finish()
    
    
    await message.answer(
        f'Ваши желания в комнате <b>{room.name}</b> изменены на:\n\n'
        f'{wish}\n\n'
        f'Санта обязательно учтет ваши пожелания! 🎅',
        reply_markup=keyboard_inline
    )
