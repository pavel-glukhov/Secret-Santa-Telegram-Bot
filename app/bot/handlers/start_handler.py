import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)
from app.bot.languages.schemes import MainSchema, RootSchema
from app.store.database.queries.users import UserRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext, session: Session):
    message = callback.message
    await state.clear()
    await root_menu(message, session)


@router.message(Command(commands=["change_language"]))
async def select_language(message: types.Message, list_languages):
    language_dict = {lang.upper(): f"select_lang_{lang}" for lang in list_languages}
    keyboard_inline = generate_inline_keyboard(language_dict)
    
    message_text = "Для начала выберите язык бота.\n\n" \
                   "First, select the language of the bot."
    await message.answer(text=message_text, reply_markup=keyboard_inline)


@router.callback_query(F.data.startswith('select_lang_'))
async def update_language(callback: types.CallbackQuery, session: Session):
    language = callback.data[12:]
    await UserRepo(session).update_user(user_id=callback.message.chat.id, language=language)
    keyboard_inline = generate_inline_keyboard({"Продолжить": "root_menu"})
    # TODO перенести текст в словарь
    message_text = f"Вы установили язык <b>{language.upper()}</b>. " \
                   f"Для начала работы с ботом нажмите 'Продолжить'"
    await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext, session: Session, language: MainSchema,
                list_languages: RootSchema):
    if not language:
        await select_language(message, list_languages)
        return
    await state.clear()
    message_text = language.messages.main_menu.start_message
    
    await message.answer(text=message_text)
    await root_menu(message, session=session, language=language, edit_message=False)


async def create_user_or_enable(message: types.Message, session: Session):
    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    user, created = await UserRepo(session).get_or_create(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    if created:
        logger.info(f'The new user "{user_id}" has been created')
    
    if not user.is_active:
        await UserRepo(session).enable_user(message.chat.id)
        logger.info(f'The new user "{user_id}" has been enabled')
    return user


@router.callback_query(F.data == 'root_menu')
@router.message(Command(commands=['menu']))
async def root_menu(data: types.Message | types.CallbackQuery, session: Session, language: MainSchema,
                    edit_message=True):
    message = data.message if isinstance(data, types.CallbackQuery) else data
    
    user = await create_user_or_enable(message, session)
    keyboard = await create_common_keyboards(message, session)
    
    is_profile_filled_out = all([user.encrypted_address, user.encrypted_number])
    
    text_reminder_notification_for_user = language.messages.main_menu.menu_reminder
    text_menu_message = language.messages.main_menu.menu
    
    message_text = (
        text_menu_message if is_profile_filled_out
        else text_reminder_notification_for_user + text_menu_message
    )
    
    if edit_message:
        await message.edit_text(text=message_text, reply_markup=keyboard)
    else:
        await message.answer(text=message_text, reply_markup=keyboard)


@router.callback_query(F.data == 'menu_about_game')
@router.message(Command(commands=['about']))
async def about_game(data: types.Message | types.CallbackQuery, language: MainSchema):
    message = data.message if isinstance(data, types.CallbackQuery) else data
    
    keyboard_inline = generate_inline_keyboard(
        {
            language.buttons.return_back: "root_menu",
        }
    )
    message_text = language.messages.main_menu.about_message
    
    await message.edit_text(text=message_text, reply_markup=keyboard_inline)
