import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.rooms import ChangeBudget
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_change-budget'))
async def change_room_budget(callback: types.CallbackQuery, state: FSMContext):
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)
    
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        'Укажите новый бюджет для игроков вашей комнаты '
        'на подарок Тайного Санты.\n'
        'Напиши в чат сумму в любом формате, '
        'например 2000 тенге,'
        '200 рублей или 20$\n\n'
        'Длина сообщения не должна превышать 16 символов.'
    )
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeBudget.waiting_for_budget)


@router.message(lambda message:
                len(message.text.lower()) > 16,
                StateFilter(ChangeBudget.waiting_for_budget))
async def process_change_budget_invalid(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    logger.info('long budget message'
                f' command from [{message.from_user.id}] ')
    
    message_text = (
        'Вы введи слишком длинное сообщение для бюджета.\n '
        'Длина сообщения не может быть больше 16 символов\n'
        'Для изменения вашего бюджета, отправьте новое сообщение.\n'
    )
    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@router.message(ChangeBudget.waiting_for_budget)
async def process_changing_budget(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    await message.delete()

    bot_message = state_data['bot_message_id']
    new_budget = message.text
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_config_{room_number}",
        }
    )
    await RoomRepo().update(room_number, budget=new_budget)
    
    message_text = (
        f'Бюджет для комнаты {room_number} был обновлен.\n\n'
        f'<b>Новое значение</b>: {new_budget}'
    )
    
    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.clear()
