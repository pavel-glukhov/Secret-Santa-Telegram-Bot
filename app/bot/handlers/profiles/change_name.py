import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.states.profiles_states import ChangeUserName
from app.store.database.repo.users import UserRepo

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'profile_edit_name')
async def change_username(callback: types.CallbackQuery,
                          state: FSMContext,
                          lang: TranslationMainSchema):
    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )
    message_text = lang.messages.profile_menu.change_name.change_name_first_msg

    initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeUserName.waiting_for_first_name)


@router.message(ChangeUserName.waiting_for_first_name)
async def process_changing_first_name(message: types.Message,
                                      state: FSMContext,
                                      lang: TranslationMainSchema):
    first_name = message.text
    await state.update_data(first_name=first_name)

    await message.delete()

    state_data = await state.get_data()
    bot_message = state_data['bot_message_id']

    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )

    message_text = lang.messages.profile_menu.change_name.change_name_second_msg

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.set_state(ChangeUserName.waiting_for_last_name)


@router.message(ChangeUserName.waiting_for_last_name)
async def process_changing_last_name(message: types.Message,
                                     state: FSMContext,
                                     session: AsyncSession,
                                     lang: TranslationMainSchema):
    state_data = await state.get_data()
    first_name = state_data.get('first_name')
    last_name = message.text
    user_id = message.chat.id
    bot_message = state_data.get('bot_message_id')

    await message.delete()

    return_back_button = lang.buttons.return_back_button
    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: "profile_edit",
        }
    )
    await UserRepo(session).update_user(user_id,
                                        first_name=first_name,
                                        last_name=last_name)
    logger.info(f'The user [{user_id}] updated fist and last name.')
    message_text = lang.messages.profile_menu.change_name.change_name_third_msg

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.clear()
