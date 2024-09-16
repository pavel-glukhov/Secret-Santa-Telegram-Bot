import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session
from app.bot.languages import TranslationMainSchema

from app.bot.handlers.formatters import profile_information_formatter
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.game_result import GameResultRepo
from app.store.database.queries.rooms import RoomRepo
from app.store.scheduler.operations import get_task

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_menu'))
async def my_room(callback: types.CallbackQuery,
                  session: Session,
                  app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    user_id = callback.message.chat.id

    room_repo = RoomRepo(session)
    room = await room_repo.get(room_number)
    is_room_owner = await room_repo.is_owner(user_id=user_id, room_number=room_number)

    if room.is_closed:
        await _room_is_closed(callback, room.number, user_id, session, app_text_msg)
        return

    scheduler_task = get_task(room_number)
    keyboard_dict = _generate_keyboard_dict(
        room_number, is_room_owner, scheduler_task, app_text_msg)

    message_text = _generate_message_text(room, scheduler_task, app_text_msg)

    await callback.message.edit_text(text=message_text, reply_markup=generate_inline_keyboard(keyboard_dict))


def _generate_keyboard_dict(room_number: int,
                            is_room_owner: bool,
                            scheduler_task,
                            app_text_msg: TranslationMainSchema) -> dict:
    is_not_owner_keyboard = {
        app_text_msg.buttons.room_menu.user_room_buttons.room_show_wish: f'room_show-wish_{room_number}',
        app_text_msg.buttons.room_menu.user_room_buttons.room_exit: f'room_exit_{room_number}',
        app_text_msg.buttons.return_back_button: 'root_menu',
    }

    if is_room_owner:
        start_game_button_name = (app_text_msg.buttons.room_menu.user_room_buttons.started_game
                                  if scheduler_task
                                  else app_text_msg.buttons.room_menu.user_room_buttons.start_game)
        is_not_owner_keyboard.pop(
            app_text_msg.buttons.room_menu.user_room_buttons.room_exit)

        owner_keyboard = {
            start_game_button_name: f'room_start-game_{room_number}',
            app_text_msg.buttons.room_menu.user_room_buttons.room_member_list: f'room_member-list_{room_number}',
            app_text_msg.buttons.room_menu.user_room_buttons.configuration: f'room_config_{room_number}'
        }
        owner_keyboard.update(is_not_owner_keyboard)
        return owner_keyboard
    return is_not_owner_keyboard


def _generate_message_text(room, scheduler_task, app_text_msg) -> str:
    text_control_room = app_text_msg.messages.rooms_menu.main.text_control_room.format(
        room_name=room.name,
        room_number=room.number,
        room_budget=room.budget
    )

    if scheduler_task:
        next_time_run = scheduler_task.next_run_time.strftime("%Y-%b-%d")
        text_control_room += app_text_msg.messages.rooms_menu.main.text_control_room_scheduler.format(
            next_time_run=next_time_run
        )
    else:
        text_control_room += app_text_msg.messages.rooms_menu.main.text_control_room_not_scheduler

    return text_control_room


async def _room_is_closed(callback: types.CallbackQuery,
                          room_number: int,
                          user_id: int,
                          session: Session,
                          app_text_msg: TranslationMainSchema) -> None:
    game_result_repo = GameResultRepo(session)
    room_repo = RoomRepo(session)

    game_results = await game_result_repo.get_room_id_count(room_id=room_number)
    room_owner = await room_repo.is_owner(user_id=user_id, room_number=room_number)

    if game_results <= 0:
        message_text, keyboard_dict = _generate_inactive_room_response(
            room_number, room_owner, app_text_msg)
    else:
        recipient = await game_result_repo.get_recipient(room_id=room_number, user_id=user_id)
        message_text, keyboard_dict = _generate_active_room_response(
            room_number, recipient, app_text_msg)

    await callback.message.edit_text(text=message_text, reply_markup=generate_inline_keyboard(keyboard_dict))


def _generate_inactive_room_response(room_number: int,
                                     room_owner: bool,
                                     app_text_msg: TranslationMainSchema) -> tuple[str, dict]:
    keyboard_dict = {
        app_text_msg.buttons.room_menu.user_room_buttons.room_activate: f'room_activate_{room_number}',
        app_text_msg.buttons.room_menu.user_room_buttons.configuration: f'room_config_{room_number}',
        app_text_msg.buttons.return_back_button: 'root_menu',
    }

    if not room_owner:
        del keyboard_dict[app_text_msg.buttons.room_menu.user_room_buttons.room_activate]
        del keyboard_dict[app_text_msg.buttons.room_menu.user_room_buttons.configuration]

    message_text = app_text_msg.messages.rooms_menu.main.room_closed_uns.format(
        room_number=room_number
    )

    if room_owner:
        message_text += app_text_msg.messages.rooms_menu.main.room_closed_uns_for_own

    return message_text, keyboard_dict


def _generate_active_room_response(room_number: int,
                                   recipient,
                                   app_text_msg: TranslationMainSchema) -> tuple[str, dict]:
    keyboard_dict = {
        app_text_msg.buttons.room_menu.user_room_buttons.room_closed_con_san: f'room_closed-con-san_{room_number}',
        app_text_msg.buttons.room_menu.user_room_buttons.room_closed_con_rec: f'room_closed-con-rec_{room_number}',
        app_text_msg.buttons.return_back_button: 'root_menu'
    }

    user_information = profile_information_formatter(recipient, app_text_msg)

    message_text = app_text_msg.messages.rooms_menu.main.room_closed_suc.format(
        user_information=user_information
    )
    return message_text, keyboard_dict
