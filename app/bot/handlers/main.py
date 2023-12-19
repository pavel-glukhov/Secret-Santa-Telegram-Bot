import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)
from app.config import load_config
from app.store.database.queries.users import UserDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(text_contains="cancel", state='*')
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await state.reset_state()
    await root_menu(message)


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    await state.reset_state()
    message_text = (
        "Хо-хо-хо! 🎅\n\n"
        "Вот и настало поиграть в Тайного Санту!\n\n"
        "Создай свою комнату для друзей, или подключись к существующей."
    )
    await message.answer(text=message_text)
    await root_menu(message, edit_message=False)


async def create_user_or_enable(message: types.Message):
    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    user, created = await UserDB.get_or_create(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    if created:
        logger.info(f'The new user "{user_id}" has been created')

    if not user.is_active:
        await UserDB.enable_user(message.chat.id)
        logger.info(f'The new user "{user_id}" has been enabled')

    return user, created


@dp.callback_query_handler(Text(equals='root_menu'))
@dp.message_handler(commands=['menu'], )
async def root_menu(
        data: types.Message | types.CallbackQuery,
        edit_message=True
):
    message = data.message if isinstance(
        data,
        types.CallbackQuery
    ) else data

    user, created = await create_user_or_enable(message)
    keyboard = await create_common_keyboards(message)

    is_profile_filled_out = all([user.encrypted_address, user.encrypted_number])

    text_reminder_notification_for_user = (
        '❗ <b>Не забудь обновить свои конт актные данные '
        'в настройках профиля</b>.\n\n'
        '❗ <b>Иначе Санта не сможет отправить тебе подарок.</b>\n\n'
    )
    text_menu_message = '<b>Меню</b>'

    message_text = (
        text_menu_message if is_profile_filled_out
        else text_reminder_notification_for_user + text_menu_message
    )

    if edit_message:
        await message.edit_text(
            text=message_text,
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            text=message_text,
            reply_markup=keyboard,
        )


@dp.callback_query_handler(Text(equals='menu_about_game'))
@dp.message_handler(commands=['about'], )
async def about_game(data: types.Message | types.CallbackQuery, ):
    message = data.message if isinstance(data, types.CallbackQuery) else data

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    #TODO добавить контакт для связи
    message_text = (
        '<b>Тайный Санта</b> - это игра, '
        'которую часто проводят перед Рождеством '
        'или Новым Годом в коллективах, семьях или среди друзей.\n'
        '  Это адаптация игры, в которой вам нужно будет вступить '
        'в одну из групп, или создать свою и пригласить своих друзей.\n'
        '  В каждой группе  каждый участник становится тайным Сантой для того, '
        'чье имя ему выпало при жеребьевке. \n'
        '  Далее, каждый тайный Санта должен приготовить для своего одариваемого '
        'подарок, оставаясь при этом анонимным.\n'
        '  Подарки необходимо будет отправить на '
        'указанный адрес полученный во время жеребьевки.\n'
        '  А в конце игры, когда все участники получит '
        'свой подарок, игроки могут раскрыть своё тайное имя и '
        'поделиться впечатлениями о подарках.\n\n'
        'Данный бот работает совершенно бесплатно.\n\n'
        'Действующие ограничения:\n'
        'Один игрок может являться владельцем только '
        f'{load_config().room.user_rooms_count} комнат.\n\n'
        '  В случае возникновения ошибок, или вопросов, '
        'вы можете связаться с @{}\n\n'
    )

    await message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
