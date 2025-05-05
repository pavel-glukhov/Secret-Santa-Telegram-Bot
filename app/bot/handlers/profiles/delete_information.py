import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.states.profiles_states import DeleteUserInformation
from app.store.database.repo.users import UserRepo

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'profile_edit_delete_all')
async def delete_user_information(callback: types.CallbackQuery,
                                  state: FSMContext,
                                  lang: TranslationMainSchema):
    confirm_button = lang.buttons.confirm_button
    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {
            confirm_button: 'confirm_deletion',
            cancel_button: 'cancel_deletion'
        }
    )
    message_text = lang.messages.profile_menu.delete_information.delete_information_first_msg

    initial_bot_message = await callback.message.edit_text(text=message_text,
                                                           reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(DeleteUserInformation.waiting_for_conformation)


@router.callback_query(F.data == 'confirm_deletion',
                      StateFilter(DeleteUserInformation.waiting_for_conformation))
async def process_deleting_information(callback: types.CallbackQuery,
                                      state: FSMContext,
                                      session: Session,
                                      lang: TranslationMainSchema):
    user_id = callback.message.chat.id
    state_data = await state.get_data()

    bot_message = state_data['bot_message_id']
    data = {
        'first_name': None,
        'last_name': None,
        'email': None,
        'encrypted_address': None,
        'encrypted_number': None,
    }
    await UserRepo(session).update_user(user_id=user_id, **data)
    logger.info(f'The user [{user_id}] deleted personal information.')

    return_back_button = lang.buttons.return_back_button
    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: "menu_user_profile",
        }
    )
    message_text = lang.messages.profile_menu.delete_information.delete_information_second_msg

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.clear()


@router.callback_query(F.data == 'cancel_deletion',
                      StateFilter(DeleteUserInformation.waiting_for_conformation))
async def cancel_deleting_information(callback: types.CallbackQuery,
                                     state: FSMContext,
                                     lang: TranslationMainSchema):
    state_data = await state.get_data()
    bot_message = state_data['bot_message_id']

    return_back_button = lang.buttons.return_back_button
    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: "menu_user_profile",
        }
    )
    message_text = lang.messages.profile_menu.delete_information.cancel_message

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.clear()