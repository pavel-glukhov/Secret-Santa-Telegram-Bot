import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomDB

logger = logging.getLogger(__name__)


class CreateRoom(StatesGroup):
    waiting_for_room_name = State()
    waiting_for_room_budget = State()
    waiting_for_room_wishes = State()


@dp.callback_query_handler(Text(equals='menu_create_new_room'))
async def create_room(callback: types.CallbackQuery, ):
    await CreateRoom.waiting_for_room_name.set()
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )

    await callback.message.edit_text(
        'Хо-хо-хо! 🎅\n\n'
        'Как ты хочешь назвать свою комнату?\n'
        'Напиши мне ее название и мы пойдем дальше\n\n'
        'Имя комнаты не должно превышать 12 символов.\n',
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_name)
async def process_name(message: types.Message, state: FSMContext):
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    room_name = message.text
    await state.update_data(room_name=room_name)

    if not len(room_name) < 13:
        keyboard_inline = generate_inline_keyboard(
            {
                "Отмена": 'cancel',
            }
        )
        return await message.answer(
            text='Вы ввели слишком длинное имя, '
                 'пожалуйста придумайте другое.\n'
                 'Имя комнаты не должно превышать 12 символов.\n',
            reply_markup=keyboard_inline
        )
    await CreateRoom.next()

    await message.answer(
        f'Принято! Имя твоей комнаты <b>{room_name}</b>\n\n'
        'А теперь укажи максимальный бюджет '
        'на подарок Тайного Санты.\n'
        'Напиши в чат сумму в любом формате, '
        'например 2000 тенге,'
        '200 руб или 20$\n',
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_budget)
async def process_budget(message: types.Message, state: FSMContext):
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )

    room_budget = message.text
    await state.update_data(room_budget=room_budget)

    await CreateRoom.next()

    await message.answer(
        f'Принято! Ваш бюджет будет составлять <b>{room_budget}</b>\n\n'
        'И последний вопрос.\n'
        'Напиши свои пожелания по подарку. '
        'Возможно у тебя есть хобби и '
        'ты хочешь получить что-то особое?\n',
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_wishes)
async def process_wishes(message: types.Message, state: FSMContext):
    user_wishes = message.text
    data = await state.get_data()

    keyboard_inline = generate_inline_keyboard(
        {
            "Меню ◀️": 'root_menu',
        }
    )

    room = await RoomDB.create(user_wish=user_wishes,
                               owner=message.chat.id,
                               name=data['room_name'],
                               budget=data['room_budget'])

    logger.info(f'The new room "{room.number}" '
                f'has been created by {message.chat.id}')

    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        f'Комната <b>"{room.name}"</b> создана.\n'
        f'Держи номер комнаты <b>{room.number}</b>\n'
        f'Этот код нужно сообщить своим друзьям, '
        f'что бы они присоединились '
        f'к твоей игре.\n\n',
    )

    await message.answer(
        "А пока ты можешь вернуться назад и обновить свой профиль",
        reply_markup=keyboard_inline,
    )
    await state.finish()
