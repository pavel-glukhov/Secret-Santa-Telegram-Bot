import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.store.database import user_db
from app.bot.keyborads.common import generate_inline_keyboard

logger = logging.getLogger(__name__)


class DeleteUserInformation(StatesGroup):
    waiting_for_conformation = State()


@dp.callback_query_handler(Text(equals='profile_edit_delete_all'))
async def delete_user_information(callback: types.CallbackQuery):
    message = callback.message
    await DeleteUserInformation.waiting_for_conformation.set()

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    await message.answer(
        'Напиши *подтверждаю* для удаления твоих данных из профиля.\n\n'
        ,
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
    return await message.reply(
        'Вы ввели неверную команду для подтверждения, попробуйте снова.\n',
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
        'address': None,
        'contact_number': None
    }

    await user_db().update_user(user_id=user_id, **data)

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"menu_user_profile",
        }
    )
    await message.answer(
        'Все данные о вас были удалены.\n\n',
        reply_markup=keyboard_inline
    )
    await state.finish()
