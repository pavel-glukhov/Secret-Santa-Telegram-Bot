from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import user_db

from app.keyborads.common import keyboard_button


class DeleteUserInformation(StatesGroup):
    waiting_for_conformation = State()


async def delete_user_information(message: types.Message):
    await DeleteUserInformation.waiting_for_conformation.set()

    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')
    await message.answer(
        'Напиши *подтверждаю* для удаления твоих данных из профиля.\n\n'
        ,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message:
                    message.text.lower() != 'подтверждаю',
                    state=DeleteUserInformation.waiting_for_conformation)
async def process_deleting_information_invalid(message: types.Message):
    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')
    return await message.reply(
        'Вы ввели неверную команду для подтверждения, попробуйте снова.\n',
        parse_mode=ParseMode.MARKDOWN,
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

    await user_db().update_user(
        user_id=user_id, **data

    )
    keyboard_inline = keyboard_button(text="Вернуться назад ◀️",
                                      callback=f"menu_user_profile")
    await message.answer(
        '*Все данные о вас были удалены.*\n\n'
        ,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )
    await state.finish()
