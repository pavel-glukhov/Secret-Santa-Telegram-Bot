import logging

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.formatters import profile_information_formatter
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.core.database.repo.game_result import GameResultRepo
from app.core.database.repo.rooms import RoomRepo
from app.core.scheduler.operations import TaskScheduler

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_menu'))
async def my_room(callback: types.CallbackQuery,
                  session: AsyncSession,
                  lang: TranslationMainSchema,
                  room_number: int):
    user_id = callback.message.chat.id

    room_repo = RoomRepo(session)
    room = await room_repo.get(room_number)
    is_room_owner = await room_repo.is_owner(user_id=user_id, room_number=room_number)

    if room.is_closed:
        await _room_is_closed(callback, room.number, user_id, session, lang)
        return

    scheduler_task = TaskScheduler().get_task(room_number)
    keyboard_dict = _generate_keyboard_dict(
        room_number, is_room_owner, scheduler_task, lang)

    message_text = _generate_message_text(room, scheduler_task, lang)

    await callback.message.edit_text(
        text=message_text,
        reply_markup=generate_inline_keyboard(keyboard_dict)
    )


def _generate_keyboard_dict(room_number: int,
                            is_room_owner: bool,
                            scheduler_task,
                            lang: TranslationMainSchema) -> dict:
    show_wishes_button = lang.buttons.room_menu.user_room_buttons.room_show_wish
    leave_room_button = lang.buttons.room_menu.user_room_buttons.room_exit
    return_back_button = lang.buttons.return_back_button

    is_not_owner_keyboard = {
        show_wishes_button: f'room_show-wish_{room_number}',
        leave_room_button: f'room_exit_{room_number}',
        return_back_button: 'root_menu',
    }

    if is_room_owner:
        is_not_owner_keyboard.pop(
            lang.buttons.room_menu.user_room_buttons.room_exit)

        start_game_button_name = (lang.buttons.room_menu.user_room_buttons.started_game
                                  if scheduler_task
                                  else lang.buttons.room_menu.user_room_buttons.start_game)
        member_list_button =  lang.buttons.room_menu.user_room_buttons.room_member_list
        room_settings_button = lang.buttons.room_menu.user_room_buttons.configuration

        owner_keyboard = {
            start_game_button_name: f'room_start-game_{room_number}',
            member_list_button: f'room_member-list_{room_number}',
            room_settings_button: f'room_config_{room_number}'
        }
        owner_keyboard.update(is_not_owner_keyboard)
        return owner_keyboard
    return is_not_owner_keyboard


def _generate_message_text(room, scheduler_task, lang) -> str:
    text_control_room = lang.messages.rooms_menu.main.text_control_room.format(
        room_name=room.name,
        room_number=room.number,
        room_budget=room.budget
    )

    if scheduler_task:
        next_time_run = scheduler_task.next_run_time.strftime("%Y-%b-%d")
        text_control_room += lang.messages.rooms_menu.main.text_control_room_scheduler.format(
            next_time_run=next_time_run
        )
    else:
        text_control_room += lang.messages.rooms_menu.main.text_control_room_not_scheduler

    return text_control_room


async def _room_is_closed(callback: types.CallbackQuery,
                          room_number: int,
                          user_id: int,
                          session: AsyncSession,
                          lang: TranslationMainSchema) -> None:
    game_result_repo = GameResultRepo(session)
    room_repo = RoomRepo(session)

    game_results = await game_result_repo.get_room_id_count(room_id=room_number)
    room_owner = await room_repo.is_owner(user_id=user_id, room_number=room_number)

    if game_results <= 0:
        message_text, keyboard_dict = _generate_inactive_room_response(
            room_number, room_owner, lang)
    else:
        recipient = await game_result_repo.get_recipient(room_id=room_number, user_id=user_id)
        message_text, keyboard_dict = _generate_active_room_response(
            room_number, recipient, lang)

    await callback.message.edit_text(text=message_text, reply_markup=generate_inline_keyboard(keyboard_dict))


def _generate_inactive_room_response(room_number: int,
                                     room_owner: bool,
                                     lang: TranslationMainSchema) -> tuple[str, dict]:

    activate_room_button = lang.buttons.room_menu.user_room_buttons.room_activate
    room_settings_button = lang.buttons.room_menu.user_room_buttons.configuration
    return_back_button = lang.buttons.return_back_button

    keyboard_dict = {
        activate_room_button: f'room_activate_{room_number}',
        room_settings_button: f'room_config_{room_number}',
        return_back_button: 'root_menu',
    }

    if not room_owner:
        del keyboard_dict[activate_room_button]
        del keyboard_dict[room_settings_button]

    message_text = lang.messages.rooms_menu.main.room_closed_uns.format(
        room_number=room_number
    )

    if room_owner:
        message_text += lang.messages.rooms_menu.main.room_closed_uns_for_own

    return message_text, keyboard_dict


def _generate_active_room_response(room_number: int,
                                   recipient,
                                   lang: TranslationMainSchema) -> tuple[str, dict]:

    contact_to_santa_button = lang.buttons.room_menu.user_room_buttons.room_closed_con_san
    contact_to_recipient = lang.buttons.room_menu.user_room_buttons.room_closed_con_rec
    return_back_button = lang.buttons.return_back_button

    keyboard_dict = {
        contact_to_santa_button: f'room_closed-con-san_{room_number}',
        contact_to_recipient: f'room_closed-con-rec_{room_number}',
        return_back_button: 'root_menu'
    }

    user_information = profile_information_formatter(recipient, lang)

    message_text = lang.messages.rooms_menu.main.room_closed_suc.format(
        user_information=user_information
    )
    return message_text, keyboard_dict
