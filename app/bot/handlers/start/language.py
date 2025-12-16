import logging
import re

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.loader import language_return_dataclass
from app.core.database.repo.users import UserRepo
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "profile_language")
async def select_language(event: types.Message | types.CallbackQuery,
                          available_languages: list[str],
                          **kwargs):
    source_menu = determine_source_menu(event, kwargs.get("room_id"))
    language_dict = build_language_dict(available_languages, source_menu)
    keyboard_inline = generate_inline_keyboard(language_dict)
    message_text = get_redis_client().get("language_selection_message")

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text=message_text, reply_markup=keyboard_inline)
        await event.answer()
    else:
        await event.answer(text=message_text, reply_markup=keyboard_inline)


@router.callback_query(F.data.startswith('slct_lang_'))
async def update_language(callback: types.CallbackQuery,
                          session: AsyncSession):
    result = get_source_to_next_callback(callback.data)
    selected_language = result.get('language', 'eng')
    continue_callback = result.get('source', "root_menu")

    await UserRepo(session).update_user(
        user_id=callback.message.chat.id, language=selected_language
    )

    app_language = await language_return_dataclass(
        get_redis_client(), selected_language
    )

    keyboard_inline = generate_inline_keyboard({
        app_language.buttons.continue_button: continue_callback
    })

    message_text = app_language.messages.main_menu.select_language_answer.format(
        language=selected_language.upper()
    )

    await callback.answer()
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


def determine_source_menu(event: types.Message | types.CallbackQuery, room_id: str | None) -> str | None:
    if room_id:
        return f"inv_wlc_msg_{room_id}"
    elif isinstance(event, types.CallbackQuery):
        return "profile_edit"
    return None


def build_language_dict(available_languages: list[str], source_menu: str | None) -> dict[str, str]:
    return {
        lang.upper(): f"slct_lang_{lang}_f_{source_menu}" if source_menu else f"slct_lang_{lang}"
        for lang in available_languages
    }


def get_source_to_next_callback(string: str):
    pattern = r"slct_lang_([a-z]{2,3})(?:_f_((?:profile_edit|room_invite_\d+|inv_wlc_msg_\d+)))?"
    match = re.match(pattern, string)

    if not match:
        return {"language": None, "source": "root_menu"}

    language = match.group(1)
    source = match.group(2) if match.group(2) else "root_menu"
    return {"language": language, "source": source}
