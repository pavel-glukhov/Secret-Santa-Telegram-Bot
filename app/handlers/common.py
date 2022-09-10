import logging

from aiogram import types
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import user_db
from app.keyborads.common import create_common_keyboards, keyboard_button

logger = logging.getLogger(__name__)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Хо-хо-хо! 🎅\n\n"
        "Вот и настало поиграть в Тайного Санту!\n\n"
        "Создай свою комнату для друзей, или подключись к существующей.",
        parse_mode=ParseMode.MARKDOWN,
    )
    await root_menu(message)


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


@dp.message_handler(commands=['menu'], )
async def root_menu(message: types.Message, edit=False):
    user, created = await create_user(message)
    keyboard = await create_common_keyboards(message)
    menu_text_name = '*Меню*'
    reminder_for_user = (
        '👉 Не забудь обновить свои контактные данные '
        'в настройках профиля.\n'
        'Иначе Санта не сможет отправить тебе подарок.🙁\n\n'
    )

    is_profile_filled_out = any([user.address, user.contact_number])

    if not is_profile_filled_out:
        text = reminder_for_user + menu_text_name
    else:
        text = menu_text_name

    if edit:
        await message.edit_text(text,
                                reply_markup=keyboard,
                                parse_mode=ParseMode.MARKDOWN,
                                )
    else:
        await message.answer(text,
                             reply_markup=keyboard,
                             parse_mode=ParseMode.MARKDOWN,
                             )


@dp.message_handler(commands=['about'])
async def about_game(message: types.Message):
    keyboard_inline = keyboard_button(text="Вернуться назад ◀️",
                                      callback="root_menu")

    text = 'Это адаптированная игра "Тайный Санта"'
    await message.edit_text(text,
                            reply_markup=keyboard_inline,
                            parse_mode=ParseMode.MARKDOWN,
                            )
