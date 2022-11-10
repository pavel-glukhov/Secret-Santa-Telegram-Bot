import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.users import UserDB

logger = logging.getLogger(__name__)


class ChangeAddress(StatesGroup):
    waiting_for_address_information = State()


@dp.callback_query_handler(Text(equals='profile_edit_address'))
async def change_user_address(callback: types.CallbackQuery):
    message = callback.message
    await ChangeAddress.waiting_for_address_information.set()

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    await message.answer(
        'Для того, что бы ваш Тайный Санта смог отправить вам посылку, '
        'напишите ваш адрес куда необходимо отправить посылку'
        ' и не забудьте указать:\n\n'
        '<b>— Страну</b>\n'
        '<b>— область</b>\n'
        '<b>— город</b>\n'
        '<b>— улицу</b>\n'
        '<b>— дом</b>\n'
        '<b>— квартиру</b>\n'
        '<b>— этаж</b>*\n'
        '<b>— номер на домофоне, если отличается от квартиры</b>\n'
        '<b>— индекс</b>\n\n'
        '<b>Например: Россия, Московская область, г. Фрязино, ул. Пупкина,'
        ' д. 99, кв. 999, этаж 25, индекс 123987.</b>\n',
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangeAddress.waiting_for_address_information)
async def process_changing_owner(message: types.Message, state: FSMContext):
    address = message.text
    user_id = message.chat.id
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"menu_user_profile",
        }
    )

    if len(address) < 150:
        await UserDB.update_user(user_id, address=address)
        await message.answer(
            'Адрес изменен.',
            reply_markup=keyboard_inline,
        )
        await state.finish()
    else:
        await message.answer(
            'Адресные данные не могут превышать 150 символов. Попробуйте снова.',
            reply_markup=keyboard_inline,
    )
