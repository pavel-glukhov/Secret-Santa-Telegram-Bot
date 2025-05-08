import asyncio
import datetime
import logging
import random
from calendar import monthrange
from datetime import date

import pytz
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states.start_game_states import DateTimePicker
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.communication.result_mailing import send_result_of_game
from app.store.database.repo.rooms import RoomRepo
from app.store.database.repo.users import UserRepo
from app.store.scheduler.operations import TaskScheduler

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith('room_start-game'))
async def start_game(callback: types.CallbackQuery,
                     session: AsyncSession,
                     lang: TranslationMainSchema,
                     room_number: int):
    task = TaskScheduler().get_task(task_id=room_number)
    room_members = await RoomRepo(session).get_list_members(room_number)
    user = await UserRepo(session).get_user_or_none(callback.message.chat.id)
    timezone = user.timezone or lang.messages.game_menu.start_game.time_zone_inf

    change_datetime_button = lang.buttons.game_menu.room_change_game_dt
    change_timezone_button = lang.buttons.game_menu.change_time_zone
    return_back_button = lang.buttons.return_back_button

    keyboard = {
        change_datetime_button: f"room_change-game-dt_{room_number}",
        change_timezone_button: f"change_time_zone_{room_number}",
        return_back_button: f"room_menu_{room_number}"
    }

    if len(room_members) < 3:
        message_text = lang.messages.game_menu.start_game.count_players
        keyboard.pop(lang.buttons.game_menu.change_time_zone)
    else:
        if task:
            time_to_send = task.next_run_time.strftime("%b-%d-%Y %H:%M")
            message_text = lang.messages.game_menu.start_game.msg_to_send.format(
                time_to_send=time_to_send
            )
        else:
            message_text = lang.messages.game_menu.start_game.time_not_set.format(
                timezone=timezone
            )

    keyboard_inline = generate_inline_keyboard(keyboard)
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@router.callback_query(F.data.startswith('room_change-game-dt'))
async def start_datetime(callback: types.CallbackQuery,
                         state: FSMContext,
                         lang: TranslationMainSchema,
                         room_number: int):
    await state.update_data(room_number=room_number)
    await state.set_state(DateTimePicker.picking_date)
    today = date.today()
    await callback.message.edit_text(
        text=lang.messages.game_menu.start_game.choose_date,
        reply_markup=_generate_calendar(today.year, today.month, lang)
    )


@router.callback_query(DateTimePicker.picking_date,
                       F.data.startswith("prev_"))
async def calendar_prev(callback: CallbackQuery,
                        lang: TranslationMainSchema):
    _, year, month = callback.data.split("_")
    new_date = date(int(year), int(month), 1) - relativedelta(months=1)

    await callback.message.edit_reply_markup(
        reply_markup=_generate_calendar(new_date.year, new_date.month, lang))
    await callback.answer()


@router.callback_query(DateTimePicker.picking_date,
                       F.data.startswith("next_"))
async def calendar_next(callback: CallbackQuery,
                        lang: TranslationMainSchema):
    _, year, month = callback.data.split("_")
    new_date = date(int(year), int(month), 1) + relativedelta(months=1)

    await callback.message.edit_reply_markup(
        reply_markup=_generate_calendar(new_date.year, new_date.month, lang))
    await callback.answer()


@router.callback_query(DateTimePicker.picking_date,
                       F.data.startswith("date_"))
async def date_selected(callback: CallbackQuery,
                        state: FSMContext,
                        lang: TranslationMainSchema):
    _, year, month, day = callback.data.split("_")
    selected_date = f'{year}.{month}.{day}'
    await state.update_data(selected_date=selected_date)
    await state.set_state(DateTimePicker.picking_time)

    await callback.message.edit_text(
        text=lang.messages.game_menu.start_game.choose_date.format(
            date=datetime.datetime.strptime(selected_date, "%Y.%m.%d").date()
        ),
        reply_markup=_generate_time_ranges_keyboard(lang)
    )


@router.callback_query(DateTimePicker.picking_time,
                       F.data.startswith("time_"))
async def time_selected(callback: CallbackQuery,
                        state: FSMContext,
                        session: AsyncSession,
                        lang: TranslationMainSchema):
    semaphore = asyncio.Semaphore(1)

    user_data = await state.get_data()
    selected_date = user_data.get("selected_date")
    room_number = user_data.get("room_number")

    user = await UserRepo(session).get_user_or_none(callback.message.chat.id)
    user_timezone = user.timezone

    _, start, end = callback.data.split("_")
    random_time = _get_random_time(start, end)

    timezone = pytz.timezone(user_timezone) if user_timezone else None
    selected_date_time = datetime.datetime.strptime(
        f'{selected_date} {random_time}', "%Y.%m.%d %H:%M"
    )

    datetime_obj = _convert_datetime_with_timezone(
        selected_date_time, timezone) if timezone else selected_date_time

    current_time = (datetime.datetime.now(timezone)
                    if timezone else datetime.datetime.now())

    if datetime_obj:
        if datetime_obj > current_time:
            if task := TaskScheduler().get_task(task_id=room_number):
                task.remove()

            TaskScheduler().add_task(
                task_func=send_result_of_game,
                date_time=selected_date_time,
                task_id=room_number,
                room_number=room_number,
                semaphore=semaphore
            )

            await RoomRepo(session).update(
                room_number,
                started_at=datetime.datetime.now(),
                closed_at=None, is_closed=False
            )
            return_back_button = lang.buttons.return_back_button

            keyboard_inline = generate_inline_keyboard(
                {
                    return_back_button: f"room_menu_{room_number}"
                }
            )
            message_text = lang.messages.game_menu.start_game.time_set_to.format(
                datetime_set_to=selected_date_time.strftime("%d %b %Y %H:%M")
            )

            await callback.message.edit_text(
                text=message_text,
                reply_markup=keyboard_inline
            )

            await state.clear()
            return None

        back_to_set_datetime = lang.buttons.game_menu.room_change_game_dt
        cancel_button = lang.buttons.cancel_button

        keyboard_inline = generate_inline_keyboard(
            {back_to_set_datetime: f"room_change-game-dt_{room_number}",
             cancel_button: 'cancel'}
        )

        current_time_str = current_time.strftime("%Y.%m.%d %H:%M")
        datetime_obj_str = datetime_obj.strftime("%Y.%m.%d %H:%M")

        message_text = lang.messages.game_menu.start_game.expired_datetime.format(
            current_time_str=current_time_str,
            datetime_obj_str=datetime_obj_str
        )

        await _incorrect_data_format(callback.message, message_text,
                                     keyboard_inline)


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()


async def _incorrect_data_format(
        message: types.Message,
        text: str,
        keyboard_inline: types.InlineKeyboardMarkup) -> None:
    await message.edit_text(
        text=text,
        reply_markup=keyboard_inline
    )


def _convert_datetime_with_timezone(datetime_obj: datetime,
                                    timezone) -> datetime:
    return timezone.localize(datetime_obj)


def _generate_calendar(year: int,
                       month: int,
                       lang: TranslationMainSchema) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    month_name = date(year, month, 1).strftime("%B %Y")

    builder.row(
        InlineKeyboardButton(text="⬅️", callback_data=f"prev_{year}_{month}"),
        InlineKeyboardButton(text=month_name, callback_data="ignore"),
        InlineKeyboardButton(text="➡️", callback_data=f"next_{year}_{month}")
    )
    list_of_month_letters = lang.messages.game_menu.start_game.days_short
    builder.row(
        *[InlineKeyboardButton(
            text=d, callback_data="ignore") for d in list_of_month_letters]
    )

    first_day = date(year, month, 1)
    start_day = (first_day.weekday() + 1) % 7
    total_days = monthrange(year, month)[1]

    row = []
    for _ in range(start_day):
        row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))

    for day in range(1, total_days + 1):
        row.append(InlineKeyboardButton(text=str(day), callback_data=f"date_{year}_{month}_{day}"))
        if len(row) == 7:
            builder.row(*row)
            row = []

    if row:
        while len(row) < 7:
            row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        builder.row(*row)

    return builder.as_markup()


def _generate_time_ranges_keyboard(lang: TranslationMainSchema) -> InlineKeyboardMarkup:
    ranges = [
        ("00:00", "06:00"),
        ("06:00", "09:00"),
        ("09:00", "12:00"),
        ("12:00", "15:00"),
        ("15:00", "18:00"),
        ("18:00", "21:00"),
        ("21:00", "00:00"),
    ]
    builder = InlineKeyboardBuilder()
    for start, end in ranges:
        label = lang.messages.game_menu.start_game.between.format(start=start, end=end)
        builder.button(text=label, callback_data=f"time_{start}_{end}")
    builder.adjust(1)
    return builder.as_markup()


def _get_random_time(start_str: str, end_str: str) -> str:
    start_hour, start_minute = map(int, start_str.split(":"))
    end_hour, end_minute = map(int, end_str.split(":"))

    start_total_minutes = start_hour * 60 + start_minute
    end_total_minutes = end_hour * 60 + end_minute
    if end_total_minutes <= start_total_minutes:
        end_total_minutes += 24 * 60

    random_minutes = random.randint(start_total_minutes, end_total_minutes - 1)
    random_hour = (random_minutes // 60) % 24
    random_minute = random_minutes % 60

    return f"{random_hour:02d}:{random_minute:02d}"
