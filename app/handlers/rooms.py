import re

from aiogram.dispatcher.filters import Text

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.database.operations import RoomDB
from app import dispatcher as dp
from aiogram.types.message import ParseMode

from app.keyborads.common import create_common_keyboards


class CreateRoom(StatesGroup):
    waiting_for_room_name = State()
    waiting_for_room_budget = State()
    waiting_for_room_notes = State()


class JoinRoom(StatesGroup):
    waiting_for_room_number = State()


class DeleteRoom(StatesGroup):
    waiting_for_room_number = State()


@dp.message_handler(state='*', commands='отмена')
@dp.message_handler(Text(equals='отмена',
                         ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    keyboard = await create_common_keyboards(message)
    await state.finish()
    await message.answer("Действие отменено",
                         reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Создать комнату 🔨",
                    state=None)
async def create_room(message: types.Message):
    await CreateRoom.waiting_for_room_name.set()
    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Как ты хочешь назвать свою комнату?\n'
        'Напиши мне ее название и мы пойдем дальше\n\n'
        'Что бы отменить процесс, введите в чате *отмена*',
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
        'Что бы отменить процесс, введите в чате *отмена*',
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
        'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_notes)
async def process_notes(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_notes'] = message.text

    await state.finish()

    room = await RoomDB().create_room(user_note=data['user_notes'],
                                      owner=message.chat.id,
                                      name=data['room_name'],
                                      budget=data['room_budget'])

    keyboard = await create_common_keyboards(message)

    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        f'Комната *"{room.name}"*'
        f'создана. \n'
        f'Держи номер комнаты *{room.number}*\n'
        f'Этот код нужно сообщить своим друзьям, '
        f'что бы они присоединились '
        f'к твоей игре.\n\n',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )


@dp.message_handler(lambda message: message.text == "Войти в комнату 🏠",
                    state=None)
async def join_room(message: types.Message):
    await JoinRoom.waiting_for_room_number.set()
    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Введи номер комнаты в которую ты хочешь зайти.\n\n'
        'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(state=JoinRoom.waiting_for_room_number)
async def joined_room(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_number'] = message.text

    if isinstance(int, data['room_number']):
        result = await RoomDB().add_member(
            user_id=message.chat.id,
            room_number=data['room_number']
        )
    else:
        result = False

    keyboard = await create_common_keyboards(message)

    await state.finish()
    if result:
        await message.answer(
            '"Хо-хо-хо! 🎅\n\n'
            'Теперь ты можешь поиграть',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    else:
        await message.answer(
            'Вы ввели несуществующий номер комнаты, попробуйте снова',
            parse_mode=ParseMode.MARKDOWN,
        )


@dp.message_handler(lambda message: message.text.startswith("Ваша комната:"))
async def my_room(message: types.Message):
    number_room = re.findall(r'\d{6}', message.text)[0]
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
            text="Выйти из комнаты 🚪",
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


@dp.message_handler(state=None)
async def delete_room(message: types.Message, room_number: int):
    await DeleteRoom.waiting_for_room_number.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    await message.edit_text(
        f'Для подтверждения удаления комнаты {room_number}, '
        f'введите в чат *подтверждаю*.\n\n '
        'Что бы отменить удаление, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(state=DeleteRoom.waiting_for_room_number)
async def answer_delete_room(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['confirmation'] = message.text.lower()

    if data['confirmation'] == 'подтверждаю':
        await RoomDB().delete_room(room_number=data['room_number'])

        keyboard = await create_common_keyboards(message)

        await message.answer(
            'Комната успешно удалена\n\n'
            'Вы можете создать новую комнату в меню ниже',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )

    else:
        # TODO добавить состояние возврата
        await message.answer(
            'Вы ввели неверную команду для подтверждения, попробуйте снова.',
            parse_mode=ParseMode.MARKDOWN,
        )
    await state.finish()
