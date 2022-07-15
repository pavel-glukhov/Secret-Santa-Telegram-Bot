import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.database.config import async_session
from app.database.operations import RoomDB, UserDB
from app import dispatcher as dp, bot
import random
from aiogram.types.message import ParseMode


class CreateRoom(StatesGroup):
    waiting_for_room_name = State()
    waiting_for_room_budget = State()
    waiting_for_room_notes = State()


@dp.message_handler(lambda message: message.text == "Создать комнату 🔨")
async def create_room(message: types.Message):
    await CreateRoom.waiting_for_room_name.set()
    await message.answer('"Хо-хо-хо! 🎅\n\n'
                         'Как ты хочешь назвать свою комнату?\n'
                         'Напиши мне ее название и мы пойдем дальше')


@dp.message_handler(state=CreateRoom.waiting_for_room_name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_name'] = message.text

    await CreateRoom.next()
    await message.answer('Принято!\n\n'
                         'А теперь укажи максимальный бюджет '
                         'на подарок Тайного Санты.\n'
                         'Напиши в чат сумму в любом формате, '
                         'например 2000 тенге,'
                         '200 руб или 20$')


@dp.message_handler(state=CreateRoom.waiting_for_room_budget)
async def process_budget(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_budget'] = message.text

    await CreateRoom.next()
    await message.answer('Принято!\n\n'
                         'Напиши свои пожелания по подарку. '
                         'Возможно у тебя есть хобби и '
                         'ты хочешь получить что-то особое?'
                         )


@dp.message_handler(state=CreateRoom.waiting_for_room_notes)
async def process_notes(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_notes'] = message.text
        logging.info('11111111111111111111111111111111')
        async with async_session() as db_session:
            async with db_session.begin():
                room = await RoomDB(db_session).create_room(
                    name=data['room_name'],
                    owner_id=message.chat.id,
                    budget=data['room_budget'],
                    user_note=data['user_notes']
                )
        logging.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        await message.answer('"Хо-хо-хо! 🎅\n\n'
                             f'Комната *"{room.name}"*'
                             f'создана. \n'
                             f'Держи номер комнаты *{room.number}*\n'
                             f'Этот код нужно сообщить своим друзьям, '
                             f'что бы они присоединились '
                             f'к твоей игре.',
                             parse_mode=ParseMode.MARKDOWN
                             )
        await state.finish()


@dp.message_handler(lambda message: message.text == "Войти в комнату 🏠")
async def join_room(message: types.Message):
    await message.answer('Нажата кнопка "Создать комнату 🔨"')
