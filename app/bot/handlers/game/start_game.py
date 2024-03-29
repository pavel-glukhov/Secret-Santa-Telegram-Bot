import asyncio
import logging
import re
from datetime import datetime

import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.game.states import StartGame
from app.bot.handlers.operations import delete_user_message, get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.messages.result_mailing import send_result_of_game
from app.store.queries.rooms import RoomRepo
from app.store.queries.users import UserRepo
from app.store.scheduler.operations import add_task, get_task

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_start-game'))
async def start_game(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    room_members = await RoomRepo().get_list_members(room_number)
    task = get_task(task_id=room_number)
    user = await UserRepo().get_user_or_none(callback.message.chat.id)
    timezone = user.timezone or ('⚠️ Ваш часовой пояс не задан. '
                                 'Для того, что бы задать корректное время,'
                                 ' вам нужно указать свой часовой пояс,'
                                 ' иначе будет использоваться время сервера.')
    keyboard = {
        "Изменить время 🕘": f"room_change-game-dt_{room_number}",
        "Изменить часовой пояс 🕘": f"change_time_zone_{room_number}",
        "Вернуться назад ◀️": f"room_menu_{room_number}"
    }
    
    if not len(list(room_members)) >= 3:
        message_text = (
            '<b>Для запуска игры требуется минимум '
            '3 участника игры</b>'
        )
        keyboard.pop("Изменить время 🕘")
    
    else:
        if not task:
            message_text = (
                '<b>Время не назначено</b>\n\n'
                '<b>Для запуска игры требуется минимум 3 участника игры</b>\n\n'
                f'<b>Ваш часовой пояс</b>: {timezone}'
            )
        else:
            message_text = (
                '<b>Рассылка будет выполнена:</b>'
                f' {task.next_run_time.strftime("%b-%d-%Y %H:%M")}'
            )
    
    keyboard_inline = generate_inline_keyboard(keyboard)
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.callback_query_handler(Text(startswith='room_change-game-dt'))
async def change_game_datetime(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    await StartGame.waiting_for_datetime.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        '"Хо-хо-хо! 🎅\n\n'
        'Для того, что-бы назначить время рассылки, '
        'отправь сообщение в формате\n'
        '<b>yyyy.mm.dd h:m</b> - <b>год.месяц.день час:минуты</b>\n\n'
        '<b>Пример: 2023.12.01 12:00</b>'
    )
    
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )


def convert_datetime_with_timezone(datetime_obj: datetime,
                                   timezone) -> datetime:
    return timezone.localize(datetime_obj)


@dp.message_handler(state=StartGame.waiting_for_datetime)
async def process_waiting_datetime(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    last_message = state_data['last_message']
    text = message.text
    user = await UserRepo().get_user_or_none(message.chat.id)
    timezone = user.timezone
    semaphore = asyncio.Semaphore(1)
    await delete_user_message(message.from_user.id, message.message_id)
    cancel_keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}"
        }
    )
    if timezone:
        timezone = pytz.timezone(timezone)
        datetime_obj = convert_datetime_with_timezone(_parse_date(text),
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
            await RoomRepo().update(room_number, started_at=datetime.now(),
                                    closed_at=None, is_closed=False)
            
            message_text = (
                'Дата рассылки установлена на'
                f' {datetime_obj.strftime("%Y-%b-%d, %H:%M:%S")}'
            )
            await last_message.edit_text(
                text=message_text,
                reply_markup=keyboard_inline
            )
            await state.finish()
        else:
            current_time_str = current_time.strftime('%Y-%b-%d, %H:%M:%S')
            datetime_obj_str = datetime_obj.strftime('%Y-%b-%d, %H:%M:%S')
            message_text = (
                'Вы указали прошедшую дату. Попробуте снова и укажите '
                'правильную дату для жеребьевки. \n\n'
                f'<b>Время на сервере:</b> {current_time_str}\n'
                f'<b>Ваше указанное время:</b> {datetime_obj_str}'
            )
            
            await _incorrect_data_format(last_message, message_text,
                                         cancel_keyboard_inline)
    else:
        message_text = (
            'Вы указали неверную дату.\n\n Попробуте снова и укажите '
            'правильную дату для жеребьевки.'
        )
        await _incorrect_data_format(last_message, message_text,
                                     cancel_keyboard_inline)


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
