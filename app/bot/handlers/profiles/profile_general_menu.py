import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session

from app.bot.handlers.formatters import profile_information_formatter
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.store.database.queries.users import UserRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'menu_user_profile')
async def my_profile(callback: types.CallbackQuery,
                     session: Session,
                     app_text_msg: TranslationMainSchema):
    chat_id = callback.message.chat.id
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.profile_menu.change_profile: "profile_edit",
            app_text_msg.buttons.return_back_button: "root_menu",
        }
    )
    user = await UserRepo(session).get_user_or_none(chat_id)
    user_information = profile_information_formatter(user)

    message_text = app_text_msg.messages.profile_menu.main_menu.menu_message.format(
        user_information=user_information)
        
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@router.callback_query(F.data == 'profile_edit')
async def edit_profile(callback: types.CallbackQuery,
                       app_text_msg: TranslationMainSchema):
    message = callback.message
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.profile_menu.profile_edit_name: "profile_edit_name",
            app_text_msg.buttons.profile_menu.profile_edit_address: "profile_edit_address",
            app_text_msg.buttons.profile_menu.profile_edit_number: "profile_edit_number",
            app_text_msg.buttons.profile_menu.change_time_zone: "change_time_zone",
            app_text_msg.buttons.profile_menu.profile_edit_delete_all: "profile_edit_delete_all",
            app_text_msg.buttons.return_back_button: "menu_user_profile"
        }
    )
    message_text = app_text_msg.messages.profile_menu.main_menu.profile_edit_message

    await message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
