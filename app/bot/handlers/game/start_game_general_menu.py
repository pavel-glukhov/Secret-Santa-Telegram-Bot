import asyncio
import logging
import re
from datetime import datetime

import pytz
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.bot.messages.result_mailing import send_result_of_game
from app.bot.states.game import StartGame
from app.store.database.queries.rooms import RoomRepo
from app.store.database.queries.users import UserRepo
from app.store.scheduler.operations import add_task, get_task

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith('room_start-game'))
async def start_game(callback: types.CallbackQuery,
                     session: Session,
                     app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    room_repo = RoomRepo(session)
    user_repo = UserRepo(session)

    room_members = await room_repo.get_list_members(room_number)
    task = get_task(task_id=room_number)
    user = await user_repo.get_user_or_none(callback.message.chat.id)

    timezone = user.timezone or app_text_msg.messages.game_menu.start_game.time_zone_inf

    keyboard = {
        app_text_msg.buttons.game_menu.room_change_game_dt: f"room_change-game-dt_{room_number}",
        app_text_msg.buttons.game_menu.change_time_zone: f"change_time_zone_{room_number}",
        app_text_msg.buttons.return_back_button: f"room_menu_{room_number}"
    }

    if len(room_members) < 3:
        message_text = app_text_msg.messages.game_menu.start_game.count_players
        keyboard.pop(app_text_msg.buttons.game_menu.change_time_zone)
    else:
        if task:
            time_to_send = task.next_run_time.strftime("%b-%d-%Y %H:%M")
            message_text = app_text_msg.messages.game_menu.start_game.info_will_be_sent_msg.format(
                time_to_send=time_to_send)
        else:
            message_text = app_text_msg.messages.game_menu.start_game.time_not_set.format(
                timezone=timezone)

    keyboard_inline = generate_inline_keyboard(keyboard)
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@router.callback_query(F.data.startswith('room_change-game-dt'))
async def change_game_datetime(callback: types.CallbackQuery,
                               state: FSMContext,
                               app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)
    
    cancel_button = app_text_msg.buttons.cancel_button

    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )

    message_text = app_text_msg.messages.game_menu.start_game.start_game_first_msg
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(StartGame.waiting_for_datetime)


@router.message(StartGame.waiting_for_datetime)
async def process_waiting_datetime(message: types.Message,
                                   state: FSMContext,
                                   session: Session,
                                   app_text_msg: TranslationMainSchema):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    bot_message = state_data['bot_message_id']
    text = message.text

    await message.delete()

    user = await UserRepo(session).get_user_or_none(message.chat.id)
    timezone = user.timezone
    semaphore = asyncio.Semaphore(1)
    
    cancel_button = app_text_msg.buttons.cancel_button
    cancel_keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back_button: f"room_menu_{room_number}"
        }
    )
    if timezone:
        timezone = pytz.timezone(timezone)
        datetime_obj = _convert_datetime_with_timezone(_parse_date(text),
                                                       timezone)
        current_time = datetime.now(timezone)
    else:
        datetime_obj = _parse_date(text)
        current_time = datetime.now()

    if datetime_obj:
        if datetime_obj > current_time:
            if task := get_task(task_id=room_number):
                task.remove()

            add_task(task_func=send_result_of_game, date_time=datetime_obj,
                     task_id=room_number, room_number=room_number,
                     semaphore=semaphore)

            await RoomRepo(session).update(room_number, started_at=datetime.now(),
                                           closed_at=None, is_closed=False)

            datetime_set_to = datetime_obj.strftime("%Y-%b-%d, %H:%M:%S")
            message_text = app_text_msg.messages.game_menu.start_game.time_not_set.format(
                datetime_set_to=datetime_set_to)

            await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
            await state.clear()
        else:
            current_time_str = current_time.strftime('%Y-%b-%d, %H:%M:%S')
            datetime_obj_str = datetime_obj.strftime('%Y-%b-%d, %H:%M:%S')
            message_text = app_text_msg.messages.game_menu.start_game.expired_datetime.format(
                current_time_str=current_time_str,
                datetime_obj_str=datetime_obj_str)

            await _incorrect_data_format(bot_message, message_text,
                                         cancel_keyboard_inline)
    else:
        message_text = app_text_msg.messages.game_menu.start_game.incorrect_datetime
        await _incorrect_data_format(bot_message, message_text,
                                     cancel_keyboard_inline)


def _convert_datetime_with_timezone(datetime_obj: datetime,
                                    timezone) -> datetime:
    return timezone.localize(datetime_obj)


def _parse_date(text) -> datetime | bool:
    time_format_variants = ['%Y,%m,%d,%H,%M', '%Y %m %d %H:%M',
                            '%Y.%m.%d %H:%M', '%Y\\%m\\%d %H:%M',
                            '%Y/%m/%d %H:%M', '%Y %m %d %H %M']

    pattern = (r'\d{4}[\s.,/\\]?\d{1,2}[\s.,/\\]?\d{1,2}'
               r'[\s.,/\\]?\d{1,2}[\s.,:/]?\d{1,2}')
    matches = re.findall(pattern, text)

    if matches:
        for time_str in matches:
            for fmt in time_format_variants:
                try:
                    date_time = datetime.strptime(time_str, fmt)
                    return date_time

                except ValueError:
                    pass

    return False


async def _incorrect_data_format(
        message: types.Message,
        text: str,
        keyboard_inline: types.InlineKeyboardMarkup) -> None:
    await message.edit_text(
        text=text,
        reply_markup=keyboard_inline
    )
