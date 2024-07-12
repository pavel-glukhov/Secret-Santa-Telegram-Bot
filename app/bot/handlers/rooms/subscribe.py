import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import delete_user_message
from app.bot.states.rooms import JoinRoom
from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)
from app.store.queries.rooms import RoomRepo
from app.store.queries.wishes import WishRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(equals='menu_join_room'))
async def join_room(callback: types.CallbackQuery):
    state = dp.get_current().current_state()
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
    async with state.proxy() as data:
        data['chat_id'] = callback.message.chat.id
        data['last_message'] = await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )


@dp.message_handler(state=JoinRoom.waiting_for_room_number)
async def process_room_number(message: types.Message):
    state = dp.get_current().current_state()
    await state.update_data(room_number=message.text)
    state_data = await state.get_data()
    
    last_message = state_data['last_message']
    await state.update_data(room_number=state_data['room_number'])
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    
    if not state_data['room_number'].isdigit():
        message_text = (
            'Номер комнаты может содержать только цифры, '
            'попробуйте снова.'
        )
        await delete_user_message(message.from_user.id, message.message_id)
        return await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
    
    room = await RoomRepo().get(room_number=state_data['room_number'])
    
    if not room or room.is_closed is True:
        await delete_user_message(message.from_user.id, message.message_id)
        return await _is_not_exists_room(last_message,
                                         state_data['room_number'],
                                         keyboard_inline)
    is_member_of_room = await RoomRepo().is_member(
        user_id=message.chat.id,
        room_number=state_data['room_number']
    )
    await delete_user_message(message.from_user.id, message.message_id)
    if is_member_of_room:
        keyboard_inline = await create_common_keyboards(message)
        
        message_text = 'Вы уже состоите в этой комнате.'
        
        await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        logger.info(
            f'The user[{message.from_user.id}] '
            f'already is member of the room [{state_data["room_number"]}]'
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
        
        await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
    

async def _is_not_exists_room(message, room_number, keyboard_inline):
    message_text = (
        'Введенной комнаты не существует, или игра завершена.\n'
        'Введите корректный номер комнаты.'
    )
    
    await message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    
    logger.info(
        f'Incorrect room number [{room_number}] '
        f'from [{message.from_user.id}]'
    )


@dp.message_handler(state=JoinRoom.waiting_for_wishes)
async def process_room_wishes(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    wishes = message.text
    chat_id = state_data['chat_id']
    room_number = state_data['room_number']
    last_message = state_data['last_message']
    
    await RoomRepo().add_member(
        user_id=chat_id,
        room_number=room_number
    )
    
    await WishRepo().create_wish_for_room(
        wish=wishes,
        user_id=chat_id,
        room_id=room_number
    )

    keyboard_inline = generate_inline_keyboard(
        {
            "В комнату ➡️": f"room_menu_{room_number}",
        }
    )
    await delete_user_message(message.from_user.id, message.message_id)
    message_text = (
        '"Хо-хо-хо! 🎅\n\n'
        f'Вы вошли в комнату <b>{room_number}</b>.\n'
        'Теперь ты можешь играть с своими друзьями.\n'
        'Следи за анонсами владельца комнаты.\n\n'
        'Желаю хорошей игры! 😋'
    )
    
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    logger.info(
        f'The user[{message.from_user.id}] '
        f'successful subscribed to the room [{state_data["room_number"]}]'
    )
    await state.finish()


#