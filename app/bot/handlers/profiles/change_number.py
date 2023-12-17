import logging
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.profiles.states import ChangePhoneNuber
from app.bot.keyborads.common import generate_inline_keyboard
from app.config import load_config
from app.store.database.queries.users import UserDB
from app.store.encryption import CryptData

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(equals='profile_edit_number'))
async def change_phone_number(callback: types.CallbackQuery):
    message = callback.message
    await ChangePhoneNuber.waiting_for_phone_number.set()

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    
    message_text = (
        'Укажите ваш номер телефона, что бы почтовые служащие '
        'смогли оповестить вас о прибывшем подарке\n'
        '<b>Укажи свой номер используя формат: +7|8(___)___-__-__ </b> \n'
        '<b>Например:</b> 8 700 111 11 11'
    )
    
    await message.answer(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangePhoneNuber.waiting_for_phone_number)
async def process_changing_owner(message: types.Message, state: FSMContext):
    phone_number = message.text
    user_id = message.chat.id
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "menu_user_profile",
        }
    )
    
    if re.search(r'(\+7|7|8)\D*\d{3}\D*\d{3}\D*\d{2}\D*\d{2}', phone_number):
        crypt = CryptData(key=load_config().encryption.key)
        encrypted_data = crypt.encrypt(data=phone_number)
        
        await UserDB.update_user(user_id, encrypted_number=encrypted_data)
        
        message_text = 'Номер изменен.'
        await message.answer(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        await state.finish()
    else:
        await message.answer(
            'Неверный формат номера, попробуйте ещё раз',
            reply_markup=keyboard_inline,
        )
