import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import delete_user_message
from app.bot.handlers.profiles.states import ChangeAddress
from app.bot.keyborads.common import generate_inline_keyboard
from app.config import load_config
from app.store.database.queries.users import UserDB
from app.store.encryption import CryptData

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(equals='profile_edit_address'))
async def change_user_address(callback: types.CallbackQuery):
    await ChangeAddress.waiting_for_address_information.set()
    state = dp.get_current().current_state()
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )

    message_text = (
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
        ' д. 99, кв. 999, этаж 25, индекс 123987.</b>\n'
    )
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.message_handler(state=ChangeAddress.waiting_for_address_information)
async def process_changing_owner(message: types.Message, state: FSMContext):
    state_data = await dp.current_state().get_data()
    last_message = state_data['last_message']
    address = message.text
    user_id = message.chat.id
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "menu_user_profile",
        }
    )
    await delete_user_message(message.from_user.id,
                              message.message_id)
    if len(address) < 150:
        crypt = CryptData(key=load_config().encryption.key)
        encrypted_data = crypt.encrypt(data=address)
        
        await UserDB.update_user(user_id, encrypted_address=encrypted_data)
        logger.info(f'The user [{user_id}] updated an address.')
        
        message_text = 'Адрес изменен.'
        
        await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        await state.finish()
    else:
        message_text = (
            'Адресные данные не могут превышать 150 символов.'
            ' Попробуйте снова.'
        )
        await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
