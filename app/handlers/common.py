import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app import dispatcher as dp
from app.database import user_db
from app.keyborads.common import (create_common_keyboards,
                                  generate_inline_keyboard)

logger = logging.getLogger(__name__)


@dp.callback_query_handler(text_contains="cancel", state='*')
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await state.reset_state()
    await message.answer('Действие отменено')
    await root_menu(message)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Хо-хо-хо! 🎅\n\n"
        "Вот и настало поиграть в Тайного Санту!\n\n"
        "Создай свою комнату для друзей, или подключись к существующей.",
    )
    await root_menu(message)


# TODO заменить это на мидлварь
async def create_user(message: types.Message):
    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name

    user, created = await user_db().get_or_create(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    if created:
        logger.info(f'The new user "{user_id}" has been created')

    return user, created


@dp.callback_query_handler(Text(equals='root_menu'), )
@dp.message_handler(commands=['menu'], )
async def root_menu(data: types.Message | types.CallbackQuery, edit_message=False):
    message = data.message if isinstance(data, types.CallbackQuery) else data

    user, created = await create_user(message)
    keyboard = await create_common_keyboards(message)
    menu_text_name = '*Меню*'

    is_profile_filled_out = all([user.address, user.contact_number])

    reminder_for_user = (
        '❗ *Не забудь обновить свои конт актные данные '
        'в настройках профиля*.\n\n'
        '❗ *Иначе Санта не сможет отправить тебе подарок.*\n\n'
    )

    text = menu_text_name if is_profile_filled_out else reminder_for_user + menu_text_name

    if edit_message:
        await message.edit_text(text, reply_markup=keyboard, )
    else:
        await message.answer(text, reply_markup=keyboard, )


@dp.callback_query_handler(Text(equals='menu_about_game'))
@dp.message_handler(commands=['about'], )
async def about_game(data: types.Message | types.CallbackQuery, ):
    message = data.message if isinstance(data, types.CallbackQuery) else data

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    text = 'Это адаптированная игра "Тайный Санта"'  # TODO добавить текст об игре
    await message.edit_text(text, reply_markup=keyboard_inline, )
