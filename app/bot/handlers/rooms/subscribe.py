import logging

from aiogram import types
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from app.bot.states.rooms import JoinRoom
from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)
from app.store.queries.rooms import RoomRepo
from app.store.queries.wishes import WishRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'menu_join_room')
async def join_room(callback: types.CallbackQuery, state: FSMContext):
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    message_text = (
        'Хо-хо-хо! 🎅\n\n'
        'Введи номер комнаты в которую ты хочешь зайти.\n'
    )
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(JoinRoom.waiting_for_room_number)


@router.message(JoinRoom.waiting_for_room_number)
async def process_room_number(message: types.Message, state: FSMContext):
    await state.update_data(room_number=message.text)
    state_data = await state.get_data()
    bot_message = state_data.get('bot_message_id')
    
    await message.delete()
    
    await state.update_data(room_number=state_data['room_number'])
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    
    if not state_data['room_number'].isdigit():
        message_text = (
            'Номер комнаты может содержать только цифры, '
            'попробуйте снова.'
        )
        return await bot_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
    
    room = await RoomRepo().get(room_number=state_data['room_number'])
    
    if not room or room.is_closed is True:
        return await _is_not_exists_room(bot_message,
                                         state_data['room_number'],
                                         keyboard_inline)
    is_member_of_room = await RoomRepo().is_member(
        user_id=message.chat.id,
        room_number=state_data['room_number']
    )
    if is_member_of_room:
        keyboard_inline = await create_common_keyboards(message)
        
        message_text = 'Вы уже состоите в этой комнате.'
        
        await bot_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        logger.info(
            f'The user[{message.from_user.id}] '
            f'already is member of the room [{state_data["room_number"]}]'
        )
        await state.clear()
    
    else:
        await state.set_state(JoinRoom.waiting_for_wishes)
        
        message_text = (
            'А теперь напишите свои пожелания к подарку. '
            'Возможно у тебя есть хобби и '
            'ты хочешь получить что-то особое?\n'
            'Ваши комментарии помогут Тайному Санте '
            'выбрать для вас подарок.\n'
        )
        
        await bot_message.edit_text(
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


@router.message(JoinRoom.waiting_for_wishes)
async def process_room_wishes(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    wishes = message.text
    chat_id = state_data['chat_id']
    room_number = state_data['room_number']
    bot_message = state_data.get('bot_message_id')
    
    await message.delete()
    
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
    message_text = (
        'Хо-хо-хо! 🎅\n\n'
        f'Вы вошли в комнату <b>{room_number}</b>.\n'
        'Теперь ты можешь играть с своими друзьями.\n'
        'Следи за анонсами владельца комнаты.\n\n'
        'Желаю хорошей игры! 😋'
    )
    
    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    logger.info(
        f'The user[{message.from_user.id}] '
        f'successful subscribed to the room [{state_data["room_number"]}]'
    )
    await state.clear()

#
