import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)
from app.store.database.queries.rooms import RoomDB
from app.store.database.queries.wishes import WishDB

logger = logging.getLogger(__name__)


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
    message_text = (
        '"Хо-хо-хо! 🎅\n\n'
        'Введи номер комнаты в которую ты хочешь зайти.\n'
    )
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.message_handler(state=JoinRoom.waiting_for_room_number)
async def process_room_number(message: types.Message):
    room_number = message.text
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    
    if not message.text.isdigit():
        message_text = (
            'Номер комнаты может содержать только цифры, '
            'попробуйте снова.'
        )
        return await message.answer(
            text=message_text,
            reply_markup=keyboard_inline,
        )
    
    is_room_exist = await RoomDB.is_exists(room_number=room_number)
    
    if not is_room_exist:
        message_text = (
            'Введенной комнаты не существует, '
            'введите корректный номер.'
        )
        await message.answer(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        logger.info(
            f'Incorrect room number [{room_number}] '
            f'from [{message.from_user.id}]'
        )
    else:
        is_member_of_room = await RoomDB.is_member(
            user_id=message.chat.id,
            room_number=room_number
        )
        
        if is_member_of_room:
            keyboard_inline = await create_common_keyboards(message)
            
            message_text = 'Вы уже состоите в этой комнате.'
            
            await message.answer(
                text=message_text,
                reply_markup=keyboard_inline,
            )
            logger.info(
                f'The user[{message.from_user.id}] '
                f'already is member of the room [{room_number}]'
            )
            await state.finish()
        
        else:
            await JoinRoom.next()
            
            message_text = (
                'А теперь напишите свои пожелания к подарку. '
                'Возможно у тебя есть хобби и '
                'ты хочешь получить что-то особое?\n'
                'Ваши комментарии помогут Тайному Санте '
                'выбрать для вас подарок.\n'
            )
            
            await message.answer(
                text=message_text,
                reply_markup=keyboard_inline,
            )


@dp.message_handler(state=JoinRoom.waiting_for_wishes)
async def process_room_wishes(message: types.Message, state: FSMContext):
    wishes = message.text
    user_id = message.chat.id
    await state.update_data(wishes=wishes)
    data = await state.get_data()
    
    await RoomDB.add_member(
        user_id=user_id,
        room_number=data['room_number']
    )
    await WishDB.update_or_create(
        wish=data['wishes'],
        user_id=user_id,
        room_id=data['room_number']
    )
    keyboard_inline = await create_common_keyboards(message)
    
    message_text = (
        '"Хо-хо-хо! 🎅\n\n'
        'Теперь ты можешь играть с своими друзьями.\n'
        'Следи за анонсами владельца комнаты.\n\n'
        'Желаю хорошей игры! 😋'
    )
    
    await message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    logger.info(
        f'The user[{message.from_user.id}] '
        f'successful subscribed to the room [{data["room_number"]}]'
    )
    await state.finish()
