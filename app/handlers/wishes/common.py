import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import bot
from app import dispatcher as dp
from app.database import room_db, wish_db
from app.keyborads.common import generate_inline_keyboard

logger = logging.getLogger(__name__)


# TODO добавить логирование
class ChangeWish(StatesGroup):
    waiting_for_wishes = State()


async def show_wishes(message: types.Message,
                      room_number: int):
    keyboard_inline = generate_inline_keyboard(
        {
            "Изменить желание ✒️": f"room_change-wish_{room_number}",
            "Вернуться назад ◀️": f"room_menu_{room_number}",

        }
    )

    user_id = message.chat.id
    wishes = await wish_db().get_wishes(user_id, room_number)

    await message.edit_text('Ваши тайные желания 🙊: \n'
                            f'{wishes.wish}\n',
                            reply_markup=keyboard_inline)


async def update_wishes(message: types.Message,
                        room_number: int):
    await ChangeWish.waiting_for_wishes.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    await message.edit_text(
        '*Напиши новое желание:*\n',
    )


@dp.message_handler(state=ChangeWish.waiting_for_wishes)
async def process_updating_wishes(message: types.Message, state: FSMContext):
    data = await dp.current_state().get_data()
    room_number = data['room_number']
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
    room = await room_db().get_room(room_number)
    await state.finish()
    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=message.message_id)
    await message.answer(
        f'Ваши желания в комнате *{room.name}* изменены на:\n\n'
        f'{wish}\n\n'
        f'Санта обязательно учтет ваши пожелания! 🎅',
        reply_markup=keyboard_inline
    )
