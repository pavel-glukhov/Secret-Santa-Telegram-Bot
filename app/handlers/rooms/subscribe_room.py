import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import room_db, wish_db
from app.keyborads.common import create_common_keyboards, keyboard_button

logger = logging.getLogger(__name__)

# TODO добавить логирование
class JoinRoom(StatesGroup):
    waiting_for_room_number = State()
    waiting_for_wishes = State()


async def join_room(message: types.Message):
    await JoinRoom.waiting_for_room_number.set()
    keyboard_inline = keyboard_button(text="Отмена", callback='cancel')
    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Введи номер комнаты в которую ты хочешь зайти.\n',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=JoinRoom.waiting_for_room_number)
async def process_room_number(message: types.Message, state: FSMContext):
    room_number = message.text
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    user_id = message.chat.id
    keyboard_inline = keyboard_button(text="Отмена", callback='cancel')

    is_room_exist = await room_db().is_exists(room_number=room_number)

    if not is_room_exist:
        await message.answer(
            'Введенной комнаты не существует.',
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        is_member_of_room = await room_db().is_member(user_id=user_id,
                                                      room_number=room_number)

        if is_member_of_room:
            keyboard_inline = await create_common_keyboards(message)
            await message.answer(
                'Вы уже состоите в этой комнате.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard_inline
            )
            await state.finish()

        else:

            await JoinRoom.next()
            await message.answer(
                'А теперь напишите свои пожелания к подарку. '
                'Возможно у тебя есть хобби и '
                'ты хочешь получить что-то особое?\n'
                'Ваши комментарии помогут Тайному Санте '
                'выбрать для вас подарок.\n',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard_inline
            )


@dp.message_handler(state=JoinRoom.waiting_for_wishes)
async def process_room_wishes(message: types.Message, state: FSMContext):
    wishes = message.text
    user_id = message.chat.id
    await state.update_data(wishes=wishes)
    data = await state.get_data()

    await room_db().add_member(user_id=user_id,
                               room_number=data['room_number'])
    await wish_db().update_or_create(wish=data['wishes'],
                                     user_id=user_id,
                                     room_id=data['room_number'])
    keyboard_inline = await create_common_keyboards(message)
    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Теперь ты можешь играть с своими друзьями.\n'
        'Следи за анонсами владельца комнаты.\n\n'
        'Желаю хорошей игры! 😋',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )
    await state.finish()
