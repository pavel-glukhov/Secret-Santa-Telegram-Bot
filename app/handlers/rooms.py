import re

import sqlalchemy.databases
from aiogram.dispatcher.filters import Text

from app.keyborads.common import create_common_keyboards, check_user_rooms
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.database.config import async_session
from app.database.operations import RoomDB
from app import dispatcher as dp
from aiogram.types.message import ParseMode


class CreateRoom(StatesGroup):
    waiting_for_room_name = State()
    waiting_for_room_budget = State()
    waiting_for_room_notes = State()


class JoinRoom(StatesGroup):
    waiting_for_room_number = State()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    rooms = await check_user_rooms(message)
    keyboard = await create_common_keyboards(rooms)
    await state.finish()
    await message.reply('Создание комнаты отменено, '
                        'но ты всегда можешь начать сначала 👻',
                        reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Создать комнату 🔨",
                    state=None)
async def create_room(message: types.Message):
    await CreateRoom.waiting_for_room_name.set()
    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Как ты хочешь назвать свою комнату?\n'
        'Напиши мне ее название и мы пойдем дальше\n\n'
        'Что бы отменить процесс, напишите в чате *cancel*',
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_name'] = message.text

    await CreateRoom.next()
    await message.answer(
        'Принято!\n\n'
        'А теперь укажи максимальный бюджет '
        'на подарок Тайного Санты.\n'
        'Напиши в чат сумму в любом формате, '
        'например 2000 тенге,'
        '200 руб или 20$\n\n'
        'Что бы отменить процесс, напишите в чате *cancel*',
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_budget)
async def process_budget(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_budget'] = message.text

    await CreateRoom.next()
    await message.answer(
        'Принято!\n\n'
        'И последний вопрос.\n'
        'Напиши свои пожелания по подарку. '
        'Возможно у тебя есть хобби и '
        'ты хочешь получить что-то особое?\n\n'
        'Что бы отменить процесс, напишите в чате *cancel*',
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_notes)
async def process_notes(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    async with state.proxy() as data:
        data['user_notes'] = message.text

    await state.finish()

    async with async_session() as db_session:
        async with db_session.begin():
            room = await RoomDB(db_session).create_room(
                name=data['room_name'],
                owner=user_id,
                budget=data['room_budget'],
                user_note=data['user_notes']
            )
            rooms = await RoomDB(db_session).get_joined_in_rooms(user_id)

    keyboard = await create_common_keyboards(rooms)

    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        f'Комната *"{room.name}"*'
        f'создана. \n'
        f'Держи номер комнаты *{room.number}*\n'
        f'Этот код нужно сообщить своим друзьям, '
        f'что бы они присоединились '
        f'к твоей игре.\n\n'
        'Что бы отменить процесс, напишите в чате *cancel*',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )


# TODO
@dp.message_handler(lambda message: message.text == "Войти в комнату 🏠",
                    state=None)
async def join_room(message: types.Message):
    await JoinRoom.waiting_for_room_number.set()
    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Введи номер комнаты в которую ты хочешь зайти.\n\n'
        'Что бы отменить процесс, напишите в чате *cancel*',
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(state=JoinRoom.waiting_for_room_number)
async def joined_room(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    async with state.proxy() as data:
        data['room_number'] = message.text

    await state.finish()
    async with async_session() as db_session:
        async with db_session.begin():
            result = await RoomDB(db_session).add_member(user=user_id,
                                                         room_number=data[
                                                             'room_number']
                                                         )
    if result:
        await message.answer(
            '"Хо-хо-хо! 🎅\n\n'
            'Теперь ты можешь поиграть',
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.answer(
            'Что-то пошло не так',
            parse_mode=ParseMode.MARKDOWN,
        )


@dp.message_handler(lambda message: message.text.startswith("Ваша комната:"))
async def my_room(message: types.Message):
    number_room = re.findall(r'\d+', message.text)[0]

    keyboard_inline = types.InlineKeyboardMarkup()

    keyboard_list = [
        types.InlineKeyboardButton(
            text="Список участников 👥",
            callback_data=f"room_memblist_{number_room}"
        ),
        types.InlineKeyboardButton(
            text="Изменить имя комнаты ⚒",
            callback_data=f"room_chname_{number_room}"
        ),
        types.InlineKeyboardButton(
            text="Изменить пожелания 🎁",
            callback_data=f"room_chnotes_{number_room}"
        ), types.InlineKeyboardButton(
            text="Выйти из комнаты ❌",
            callback_data=f"room_exit_{number_room}"
        ), types.InlineKeyboardButton(
            text="Удалить комнату ❌",
            callback_data=f"room_delete_{number_room}"
        ),
    ]

    for button in keyboard_list:
        keyboard_inline.add(button)

    await message.answer(f"Ваша комната {number_room}",
                         reply_markup=keyboard_inline)


async def delete_room(message: types.Message, room_number):
    user_id = message.chat.id
    async with async_session() as db_session:
        async with db_session.begin():
            await RoomDB(db_session).delete_room(room_number=room_number)
            rooms = await RoomDB(db_session).get_joined_in_rooms(user_id)

    keyboard = await create_common_keyboards(rooms)
    await message.edit_text('Комната успешно удалена')

    await message.answer(
        'Вы можете создать новую комнату в меню ниже',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )
