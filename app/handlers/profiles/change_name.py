import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import dispatcher as dp
from app.database import user_db
from app.keyborads.common import generate_inline_keyboard

logger = logging.getLogger(__name__)


class ChangeUserName(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()


@dp.callback_query_handler(Text(equals='profile_edit_name'))
async def change_username(callback: types.CallbackQuery):
    message = callback.message
    await ChangeUserName.waiting_for_first_name.set()

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    await message.answer(
        'Хохохо, пора указать твои данные для Санты 🎅\n'
        'Учти, что оно будет использоваться для отправки подарка Сантой.\n\n'
        '*Сначала напиши свое имя*\n\n'
        ,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangeUserName.waiting_for_first_name)
async def process_changing_first_name(message: types.Message,
                                      state: FSMContext):
    first_name = message.text
    await state.update_data(first_name=first_name)

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        })

    await ChangeUserName.next()
    await message.answer(
        '*Теперь укажи свою фамилию*\n\n',
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangeUserName.waiting_for_last_name)
async def process_changing_last_name(message: types.Message,
                                     state: FSMContext):
    data = await state.get_data()
    first_name = data['first_name']
    last_name = message.text
    user_id = message.chat.id

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"menu_user_profile",
        }
    )
    await user_db().update_user(user_id,
                                first_name=first_name,
                                last_name=last_name)
    await message.answer(
        'Имя и фамилия изменены.',
        reply_markup=keyboard_inline,
    )
    await state.finish()
