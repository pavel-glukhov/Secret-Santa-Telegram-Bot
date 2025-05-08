import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.states.rooms_states import ChangeBudget
from app.store.database.repo.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_change-budget'))
async def change_room_budget(callback: types.CallbackQuery,
                             state: FSMContext,
                             lang: TranslationMainSchema,
                             room_number: int):
    await state.update_data(room_number=room_number)

    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )
    message_text = lang.messages.rooms_menu.change_budget.change_budget_first_msg

    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeBudget.waiting_for_budget)


@router.message(lambda message:
                len(message.text.lower()) > 16,
                StateFilter(ChangeBudget.waiting_for_budget))
async def process_change_budget_invalid(message: types.Message,
                                        state: FSMContext,
                                        lang: TranslationMainSchema):
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']

    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )
    logger.info('long budget message'
                f' command from [{message.from_user.id}] ')

    message_text = lang.messages.rooms_menu.change_budget.long_budget

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(ChangeBudget.waiting_for_budget)
async def process_changing_budget(message: types.Message,
                                  state: FSMContext,
                                  session: AsyncSession,
                                  lang: TranslationMainSchema):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    await message.delete()

    bot_message = state_data['bot_message_id']
    new_budget = message.text

    return_back_button = lang.buttons.return_back_button
    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: f"room_config_{room_number}",
        }
    )
    await RoomRepo(session).update(room_number, budget=new_budget)

    message_text = lang.messages.rooms_menu.change_budget.change_budget_second_msg.format(
        room_number=room_number,
        new_budget=new_budget
    )

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.clear()
