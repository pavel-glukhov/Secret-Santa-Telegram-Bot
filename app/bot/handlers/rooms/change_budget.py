import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.bot.states.rooms import ChangeBudget
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_change-budget'))
async def change_room_budget(callback: types.CallbackQuery,
                             state: FSMContext,
                             app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)

    cancel_button = app_text_msg.buttons.cancel_button
    
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )
    message_text = app_text_msg.messages.rooms_menu.change_budget.change_budget_first_msg

    initial_bot_message = await callback.message.edit_text(text=message_text,
                                                           reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeBudget.waiting_for_budget)


@router.message(lambda message:
                len(message.text.lower()) > 16,
                StateFilter(ChangeBudget.waiting_for_budget))
async def process_change_budget_invalid(message: types.Message,
                                        state: FSMContext,
                                        app_text_msg: TranslationMainSchema):
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    cancel_button = app_text_msg.buttons.cancel_button
    
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )
    logger.info('long budget message'
                f' command from [{message.from_user.id}] ')

    message_text = app_text_msg.messages.rooms_menu.change_budget.long_budget

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(ChangeBudget.waiting_for_budget)
async def process_changing_budget(message: types.Message,
                                  state: FSMContext,
                                  session: Session,
                                  app_text_msg: TranslationMainSchema):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    await message.delete()

    bot_message = state_data['bot_message_id']
    new_budget = message.text

    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back_button: f"room_config_{room_number}",
        }
    )
    await RoomRepo(session).update(room_number, budget=new_budget)

    message_text = app_text_msg.messages.rooms_menu.change_budget.long_budget.format(
        room_number=room_number,
        new_budget=new_budget
    )

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.clear()
