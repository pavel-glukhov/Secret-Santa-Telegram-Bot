import logging
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import user_db
from app.keyborads.common import keyboard_button

logger = logging.getLogger(__name__)


class ChangePhoneNuber(StatesGroup):
    waiting_for_phone_number = State()


async def change_phone_number(message: types.Message):
    await ChangePhoneNuber.waiting_for_phone_number.set()

    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')
    await message.answer(
        'Укажите ваш номер телефона, что бы почтовые служащие '
        'смогли оповестить вас о прибывшем подарке\n'
        '*Укажи свой номер используя формат: +7|8(___)___-__-__ * \n'
        '*Например:* 8 999 700 000 00 00',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangePhoneNuber.waiting_for_phone_number)
async def process_changing_owner(message: types.Message, state: FSMContext):
    phone_number = message.text
    user_id = message.chat.id
    keyboard_inline = keyboard_button(text="Вернуться назад ◀️",
                                      callback=f"menu_user_profile")

    if re.search('(\+7|7|8)\D*\d{3}\D*\d{3}\D*\d{2}\D*\d{2}', phone_number):
        await user_db().update_user(user_id, contact_number=phone_number)
        await message.answer(
            'Номер изменен.',
            reply_markup=keyboard_inline,
        )
        await state.finish()
    else:
        await message.answer(
            'Неверный формат номера, попробуйте ещё раз',
            reply_markup=keyboard_inline,
        )
