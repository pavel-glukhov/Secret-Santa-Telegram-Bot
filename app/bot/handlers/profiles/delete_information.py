import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.profiles.states import DeleteUserInformation
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.users import UserDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(equals='profile_edit_delete_all'))
async def delete_user_information(callback: types.CallbackQuery):
    message = callback.message
    await DeleteUserInformation.waiting_for_conformation.set()

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    message_text = (
        'Напиши <b>подтверждаю</b> для удаления твоих данных из профиля.\n\n'
    )

    await message.answer(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message:
                    message.text.lower() != 'подтверждаю',
                    state=DeleteUserInformation.waiting_for_conformation)
async def process_deleting_information_invalid(message: types.Message):
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    
    message_text = (
        'Вы ввели неверную команду для подтверждения, '
        'попробуйте снова.\n'
    )
    return await message.answer(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message:
                    message.text.lower() == 'подтверждаю',
                    state=DeleteUserInformation.waiting_for_conformation)
async def process_deleting_information(message: types.Message,
                                       state: FSMContext):
    user_id = message.chat.id

    data = {
        'first_name': None,
        'last_name': None,
        'email': None,
        'encrypted_address': None,
        'encrypted_number': None,
    }

    await UserDB.update_user(user_id=user_id, **data)

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "menu_user_profile",
        }
    )
    
    message_text = 'Все данные о вас были удалены.\n\n'
    
    await message.answer(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await state.finish()
