import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.handlers import texts
from app.store.database import room_db, wish_db
from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)

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
    
    await callback.message.edit_text(
        texts.SUBSCRIBE_MAIN_QUESTION,
        reply_markup=keyboard_inline
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
        return await message.answer(
            texts.SUBSCRIBE_IS_NOT_DIGIT,
            reply_markup=keyboard_inline
        )
    
    is_room_exist = await room_db().is_exists(room_number=room_number)
    
    if not is_room_exist:
        await message.answer(
            texts.SUBSCRIBE_INCORRECT_ROOM_NUMBER,
            reply_markup=keyboard_inline
        )
        logger.info(f'Incorrect room number [{room_number}] '
                    f'from [{message.from_user.id}]')
    else:
        is_member_of_room = await room_db().is_member(user_id=message.chat.id,
                                                      room_number=room_number)
        
        if is_member_of_room:
            keyboard_inline = await create_common_keyboards(message)
            logger.info(f'The user[{message.from_user.id}] '
                        f'already is member of the room [{room_number}]')
            await message.answer(
                texts.SUBSCRIBE_ALREADY_MEMBER,
                reply_markup=keyboard_inline
            )
            await state.finish()
        
        else:
            await JoinRoom.next()
            await message.answer(
                texts.SUBSCRIBE_WISHES,
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
        texts.SUBSCRIBE_FINAL_ANSWER,
        reply_markup=keyboard_inline
    )
    logger.info(f'The user[{message.from_user.id}] '
                f'successful subscribed to the room [{data["room_number"]}]')
    await state.finish()
