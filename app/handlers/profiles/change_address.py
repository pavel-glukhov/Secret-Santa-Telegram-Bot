import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import user_db
from app.keyborads.common import keyboard_button

logger = logging.getLogger(__name__)


class ChangeAddress(StatesGroup):
    waiting_for_address_information = State()


async def change_user_address(message: types.Message):
    await ChangeAddress.waiting_for_address_information.set()

    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')
    await message.answer(
        'Для того, что бы ваш Тайный Санта смог отправить вам посылку, '
        'напишите ваш адрес куда необходимо отправить посылку'
        ' и не забудьте указать:\n\n'
        '*— Страну*\n'
        '*— область*\n'
        '*— город*\n'
        '*— улицу*\n'
        '*— дом*\n'
        '*— квартиру*\n'
        '*— этаж*\n'
        '*— номер на домофоне, если отличается от квартиры*\n'
        '*— индекс*\n\n'
        '*Например: Россия, Московская область, г. Фрязино, ул. Пупкина,'
        ' д. 99, кв. 999, этаж 25, индекс 123987.*\n',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangeAddress.waiting_for_address_information)
async def process_changing_owner(message: types.Message, state: FSMContext):
    address = message.text
    user_id = message.chat.id
    keyboard_inline = keyboard_button(text="Вернуться назад ◀️",
                                      callback=f"menu_user_profile")

    if not address > 150:
        await user_db().update_user(user_id, address=address)
        await message.answer(
            'Адрес изменен.',
            reply_markup=keyboard_inline,
        )
        await state.finish()
    await message.answer(
        'Адресные данные не могут превышать 150 символов. Попробуйте снова.',
        reply_markup=keyboard_inline,
    )
