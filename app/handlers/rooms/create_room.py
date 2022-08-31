from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import bot
from app.database import room_db
from app.keyborads.common import create_common_keyboards


class CreateRoom(StatesGroup):
    waiting_for_room_name = State()
    waiting_for_room_budget = State()
    waiting_for_room_wishes = State()


async def create_room(message: types.Message, state: FSMContext):
    await CreateRoom.waiting_for_room_name.set()
    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Как ты хочешь назвать свою комнату?\n'
        'Напиши мне ее название и мы пойдем дальше\n\n'
        'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_name'] = message.text

    await CreateRoom.next()
    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=message.message_id)
    await message.answer(
        f'Принято! Имя твоей комнаты *{data["room_name"]}*\n\n'
        'А теперь укажи максимальный бюджет '
        'на подарок Тайного Санты.\n'
        'Напиши в чат сумму в любом формате, '
        'например 2000 тенге,'
        '200 руб или 20$\n\n'
        'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


async def process_budget(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_budget'] = message.text

    await CreateRoom.next()
    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=message.message_id)
    await message.answer(
        f'Принято! Ваш бюджет будет составлять *{data["room_budget"]}*\n\n'
        'И последний вопрос.\n'
        'Напиши свои пожелания по подарку. '
        'Возможно у тебя есть хобби и '
        'ты хочешь получить что-то особое?\n\n'
        'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


async def process_wishes(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_wishes'] = message.text

    await state.finish()

    room = await room_db().create_room(user_wish=data['user_wishes'],
                                       owner=message.chat.id,
                                       name=data['room_name'],
                                       budget=data['room_budget'])

    keyboard = await create_common_keyboards(message)
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
        reply_markup=keyboard
    )
