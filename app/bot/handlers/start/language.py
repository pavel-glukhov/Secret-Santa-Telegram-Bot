import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.loader import language_return_dataclass
from app.store.database.repo.users import UserRepo
from app.store.redis import get_redis_client

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda c: c.data == "profile_language")
async def select_language(event: types.Message | types.CallbackQuery, available_languages: list):
    is_callback = isinstance(event, types.CallbackQuery)
    source_menu = "profile" if is_callback else None

    language_dict = {
        lang.upper(): f"select_lang_{lang}_from_{source_menu}" if source_menu else f"select_lang_{lang}"
        for lang in available_languages
    }

    if source_menu:
        language_dict["Назад"] = f"back_to_{source_menu}"

    keyboard_inline = generate_inline_keyboard(language_dict)
    message_text = get_redis_client().get('language_selection_message')

    if is_callback:
        await event.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )
        await event.answer()
    else:
        await event.answer(
            text=message_text,
            reply_markup=keyboard_inline
        )


@router.callback_query(F.data.startswith('select_lang_'))
async def update_language(callback: types.CallbackQuery, session: Session):
    callback_parts = callback.data.split('_')
    selected_language = callback_parts[2]
    source_menu = (callback_parts[4]
                   if len(callback_parts) > 4
                      and callback_parts[3] == 'from' else None)

    await UserRepo(session).update_user(
        user_id=callback.message.chat.id, language=selected_language
    )

    app_language = await language_return_dataclass(get_redis_client(), selected_language)
    continue_button = app_language.buttons.continue_button
    continue_callback = "profile_edit" if source_menu == "profile" else "root_menu"

    keyboard_inline = generate_inline_keyboard(
        {continue_button: continue_callback}
    )
    message_text = app_language.messages.main_menu.select_language_answer.format(
        language=selected_language.upper()
    )
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await callback.answer()