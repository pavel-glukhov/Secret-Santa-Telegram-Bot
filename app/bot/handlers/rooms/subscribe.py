import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.store.database import room_db, wish_db
from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)

logger = logging.getLogger(__name__)


# TODO добавить логирование
class JoinRoom(StatesGroup):
    waiting_for_room_number = State()
    waiting_for_wishes = State()


@dp.callback_query_handler(Text(equals='menu_join_room'))
async def join_room(callback: types.CallbackQuery):
    await JoinRoom.waiting_for_room_number.set()
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    await callback.message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Введи номер комнаты в которую ты хочешь зайти.\n',
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=JoinRoom.waiting_for_room_number)
async def process_room_number(message: types.Message, state: FSMContext):
    room_number = message.text
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    
    user_id = message.chat.id
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    
    is_room_exist = await room_db().is_exists(room_number=room_number)
    
    if not is_room_exist:
        await message.answer(
            'Введенной комнаты не существует.',
        )
    else:
        is_member_of_room = await room_db().is_member(user_id=user_id,
                                                      room_number=room_number)
        
        if is_member_of_room:
            keyboard_inline = await create_common_keyboards(message)
            await message.answer(
                'Вы уже состоите в этой комнате.',
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
        reply_markup=keyboard_inline
    )
    await state.finish()
