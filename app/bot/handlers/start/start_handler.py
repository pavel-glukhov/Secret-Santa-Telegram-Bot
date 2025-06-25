import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.rooms.subscribe import join_to_room_inv_welcome_message
from app.bot.handlers.start.language import select_language
from app.bot.keyborads.common import create_common_keyboards
from app.bot.languages.schemes import TranslationMainSchema
from app.core.database.repo.users import UserRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: types.CallbackQuery,
                         state: FSMContext,
                         session: AsyncSession,
                         lang: TranslationMainSchema):
    await state.clear()
    await root_menu(callback.message, session, lang)


@router.callback_query(F.data == 'start_menu')
@router.message(Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext,
                session: AsyncSession,
                lang: TranslationMainSchema,
                available_languages: list):
    await state.clear()

    if payload_data := check_payload(message):
        await room_invitation(payload_data, lang, message, session, available_languages)
        return None

    if not lang:
        await create_user_or_enable(message, session)
        await select_language(message, available_languages)

        return None

    await message.answer(text=lang.messages.main_menu.start_message)
    await root_menu(message, session=session, lang=lang, edit_message=False)


def check_payload(message):
    """Checking of payload data if user went to the bot via invitation url"""
    parts = message.text.split(" ", maxsplit=1)
    if len(parts) == 2:
        payload = parts[1]

        if payload.startswith("room_"):
            room_id = int(payload.removeprefix("room_"))
            return {'room_id': room_id}
    return None


async def room_invitation(data, lang, message, session, available_languages):
    room_id = data.get("room_id")

    if not lang:
        await create_user_or_enable(message, session)
        await select_language(message, available_languages, **data)
        return None
    await join_to_room_inv_welcome_message(message, lang, session, room_id)


@router.callback_query(F.data == 'root_menu')
async def root_menu(data: types.Message | types.CallbackQuery,
                    session: AsyncSession,
                    lang: TranslationMainSchema,
                    edit_message=True):
    message = data.message if isinstance(data, types.CallbackQuery) else data

    user = await create_user_or_enable(message, session)
    keyboard = await create_common_keyboards(message, session, lang)
    is_profile_filled = user.encrypted_address, user.encrypted_number

    text_reminder_notification_for_user = lang.messages.main_menu.menu_reminder
    text_menu_message = lang.messages.main_menu.menu

    message_text = (
        text_menu_message if is_profile_filled
        else text_reminder_notification_for_user + text_menu_message
    )

    send = message.edit_text if edit_message else message.answer
    await send(text=message_text, reply_markup=keyboard)


async def create_user_or_enable(message: types.Message,
                                session: AsyncSession):
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
