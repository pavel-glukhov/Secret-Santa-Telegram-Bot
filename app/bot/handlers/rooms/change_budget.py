import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import delete_user_message, get_room_number
from app.bot.handlers.rooms.states import ChangeBudget
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_change-budget'))
async def change_room_budget(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    await ChangeBudget.waiting_for_budget.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        'Укажите новый бюджет для игроков вашей комнаты '
        'на подарок Тайного Санты.\n'
        'Напиши в чат сумму в любом формате, '
        'например 2000 тенге,'
        '200 рублей или 20$\n\n'
        'Длина сообщения не должна превышать 12 символов.'
    )
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )


@dp.message_handler(lambda message:
                    len(message.text.lower()) > 12,
                    state=ChangeBudget.waiting_for_budget)
async def process_change_budget_invalid(message: types.Message):
    state_data = await dp.get_current().current_state().get_data()
    last_message = state_data['last_message']
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    logger.info('long budget message'
                f' command from [{message.from_user.id}] ')
    
    await delete_user_message(message.from_user.id, message.message_id)
    
    message_text = (
        'Вы введи слишком длинное сообщение для бюджета.\n '
        'Длина сообщения не может быть больше 12 символов\n'
        'Для изменения вашего бюджета, отправьте новое сообщение.\n'
    )
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    

@dp.message_handler(state=ChangeBudget.waiting_for_budget)
async def process_changing_budget(message: types.Message, state: FSMContext):
    state_data = await dp.current_state().get_data()
    room_number = state_data['room_number']
    last_message = state_data['last_message']
    new_budget = message.text
    await delete_user_message(message.from_user.id, message.message_id)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}",
        }
    )
    
    await RoomDB.update(room_number, budget=new_budget)
    
    message_text = (
        f'Бюджет для комнаты {room_number} был обновлен.\n\n'
        f'<b>Новое значение</b>: {new_budget}'
    )
    
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.finish()