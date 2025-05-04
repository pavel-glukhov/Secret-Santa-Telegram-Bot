import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import language_return_dataclass
from app.store.database.queries.users import UserRepo
from app.store.redis import get_redis_client

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command(commands=["change_language"]))
async def select_language(message: types.Message, available_languages: list):
    language_dict = {
        lang.upper(): f"select_lang_{lang}" for lang in available_languages}
    keyboard_inline = generate_inline_keyboard(language_dict)
    message_text = get_redis_client().get('language_selection_message')

    await message.answer(text=message_text, reply_markup=keyboard_inline)


@router.callback_query(F.data.startswith('select_lang_'))
async def update_language(callback: types.CallbackQuery, session: Session):
    selected_language = callback.data[12:]
    await UserRepo(session).update_user(user_id=callback.message.chat.id, language=selected_language)
    app_language = await language_return_dataclass(get_redis_client(), selected_language)

    keyboard_inline = generate_inline_keyboard(
        {app_language.buttons.continue_button: "root_menu"})

    message_text = app_language.messages.main_menu.select_language_answer.format(
        language=selected_language.upper())

    await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)
