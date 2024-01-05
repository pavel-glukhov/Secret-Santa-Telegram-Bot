import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import bot
from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.handlers.wishes.states import ChangeWish
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.rooms import RoomRepo
from app.store.queries.wishes import WishRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_show-wish'))
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

    await message.edit_text('Ваши тайные желания 🙊: \n'
                            f'{wishes.wish}\n',
                            reply_markup=keyboard_inline)


@dp.callback_query_handler(Text(startswith='room_change-wish'))
async def update_wishes(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    await ChangeWish.waiting_for_wishes.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    await state.update_data(
        wishes_question_message_id=callback.message.message_id)

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    message_text = '<b>Напиши новое желание:</b>\n'
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )

@dp.message_handler(state=ChangeWish.waiting_for_wishes)
async def process_updating_wishes(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    room_number =  state_data['room_number']
    question_message_id = state_data['wishes_question_message_id']
    wish = message.text
    user_id = message.chat.id
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
    await state.finish()
    await bot.delete_message(chat_id=message.from_id,
                             message_id=question_message_id)
    await message.delete()
    
    message_text = (
        f'Ваши желания в комнате <b>{room.name}</b> изменены на:\n\n'
        f'{wish}\n\n'
        'Санта обязательно учтет ваши пожелания! 🎅'
    )
    await message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
