import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import bot
from app import dispatcher as dp
from app.database import room_db
from app.keyborads.common import keyboard_button

logger = logging.getLogger(__name__)


class CreateRoom(StatesGroup):
    waiting_for_room_name = State()
    waiting_for_room_budget = State()
    waiting_for_room_wishes = State()


async def create_room(message: types.Message):
    await CreateRoom.waiting_for_room_name.set()
    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')

    await message.answer(
        'Хо-хо-хо! 🎅\n\n'
        'Как ты хочешь назвать свою комнату?\n'
        'Напиши мне ее название и мы пойдем дальше\n\n'
        'Имя комнаты не должно превышать 12 символов.\n',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_name)
async def process_name(message: types.Message, state: FSMContext):
    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')
    room_name = message.text
    await state.update_data(room_name=room_name)

    if not len(room_name) < 13:
        keyboard_inline = keyboard_button(text="Отмена",
                                          callback='cancel')
        return await message.reply(
            text='Вы ввели слишком длинное имя, '
                 'пожалуйста придумайте другое.\n'
                 'Имя комнаты не должно превышать 12 символов.\n',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard_inline
        )

    await CreateRoom.next()
    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=message.message_id)

    await message.answer(
        f'Принято! Имя твоей комнаты *{room_name}*\n\n'
        'А теперь укажи максимальный бюджет '
        'на подарок Тайного Санты.\n'
        'Напиши в чат сумму в любом формате, '
        'например 2000 тенге,'
        '200 руб или 20$\n',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_budget)
async def process_budget(message: types.Message, state: FSMContext):
    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')

    room_budget = message.text
    await state.update_data(room_budget=room_budget)

    await CreateRoom.next()
    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=message.message_id)

    await message.answer(
        f'Принято! Ваш бюджет будет составлять *{room_budget}*\n\n'
        'И последний вопрос.\n'
        'Напиши свои пожелания по подарку. '
        'Возможно у тебя есть хобби и '
        'ты хочешь получить что-то особое?\n',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_wishes)
async def process_wishes(message: types.Message, state: FSMContext):
    user_wishes = message.text
    data = await state.get_data()

    keyboard_inline = keyboard_button(text="Меню ◀️",
                                      callback='root_menu')

    room = await room_db().create_room(user_wish=user_wishes,
                                       owner=message.chat.id,
                                       name=data['room_name'],
                                       budget=data['room_budget'])

    logger.info(f'The new room "{room.number}" '
                f'has been created by {message.chat.id}')

    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=message.message_id)

    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        f'Комната *"{room.name}"* создана.\n'
        f'Держи номер комнаты *{room.number}*\n'
        f'Этот код нужно сообщить своим друзьям, '
        f'что бы они присоединились '
        f'к твоей игре.\n\n',
        parse_mode=ParseMode.MARKDOWN,
    )
    await message.answer(
        "А пока ты можешь вернуться назад и обновить свой профиль",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline,
    )
    await state.finish()
