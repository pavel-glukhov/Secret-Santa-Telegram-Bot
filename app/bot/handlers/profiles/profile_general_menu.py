import logging

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.formatters import profile_information_formatter
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.store.database.repo.users import UserRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'menu_user_profile')
async def my_profile(callback: types.CallbackQuery,
                     session: AsyncSession,
                     lang: TranslationMainSchema):
    change_profile_button = lang.buttons.profile_menu.change_profile
    return_back_button = lang.buttons.return_back_button

    keyboard_inline = generate_inline_keyboard(
        {
            change_profile_button: "profile_edit",
            return_back_button: "root_menu",
        }
    )

    user = await UserRepo(session).get_user_or_none(callback.message.chat.id)
    user_information = profile_information_formatter(user, lang)

    message_text = lang.messages.profile_menu.main_menu.menu_message.format(
        user_information=user_information)

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@router.callback_query(F.data == 'profile_edit')
async def edit_profile(callback: types.CallbackQuery,
                       lang: TranslationMainSchema):
    profile_edit_name_button = lang.buttons.profile_menu.profile_edit_name
    profile_edit_address_button = lang.buttons.profile_menu.profile_edit_address
    profile_edit_number_button = lang.buttons.profile_menu.profile_edit_number
    change_time_zone_button = lang.buttons.profile_menu.change_time_zone
    profile_edit_delete_all_button = lang.buttons.profile_menu.profile_edit_delete_all
    change_language_button = lang.buttons.profile_menu.change_language
    return_back_button_button = lang.buttons.return_back_button


    keyboard_inline = generate_inline_keyboard(
        {
            profile_edit_name_button: "profile_edit_name",
            profile_edit_address_button: "profile_edit_address",
            profile_edit_number_button: "profile_edit_number",
            change_time_zone_button: "change_time_zone",
            change_language_button:"profile_language",
            profile_edit_delete_all_button: "profile_edit_delete_all",
            return_back_button_button: "menu_user_profile"
        }
    )

    message_text = lang.messages.profile_menu.main_menu.profile_edit_message

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
