import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.wishes import ChangeWish
from app.store.queries.rooms import RoomRepo
from app.store.queries.wishes import WishRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_show-wish'))
async def show_wishes(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    message = callback.message
    keyboard_inline = generate_inline_keyboard(
        {
            "Изменить желание ✒️": f"room_change-wish_{room_number}",
            "Вернуться назад ◀️": f"room_menu_{room_number}",
            
        }
    )
    
    user_id = message.chat.id
    wishes = await WishRepo().get(user_id, room_number)
    
    message_text = ('Ваши тайные желания 🙊: \n'  # TODO заменить текст
                    f'{wishes.wish}\n')
    
    await message.edit_text(text=message_text,
                            reply_markup=keyboard_inline)


@router.callback_query(F.data.startswith('room_change-wish'))
async def update_wishes(callback: types.CallbackQuery, state: FSMContext):
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)
    
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    message_text = '<b>Напиши новое желание:</b>\n'
    
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeWish.waiting_for_wishes)


@router.message(ChangeWish.waiting_for_wishes)
async def process_updating_wishes(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    bot_message = state_data['bot_message_id']
    wish = message.text
    user_id = message.chat.id
    
    await message.delete()
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}",
        }
    )
    await WishRepo().create_wish_for_room(
        wish=wish,
        user_id=user_id,
        room_id=room_number
    )
    
    room = await RoomRepo().get(room_number)
    await state.clear()
    
    message_text = (
        f'Ваши желания в комнате <b>{room.name}</b> изменены на:\n\n'
        f'{wish}\n\n'
        'Санта обязательно учтет ваши пожелания! 🎅'
    )
    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
