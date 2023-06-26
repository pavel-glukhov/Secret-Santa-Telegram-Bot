import logging
import re
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.messages.result_mailing import send_result_of_game
from app.store.database.queries.rooms import RoomDB
from app.store.scheduler.operations import add_task, get_task

logger = logging.getLogger(__name__)


class StartGame(StatesGroup):
    waiting_for_datetime = State()


@dp.callback_query_handler(Text(startswith='room_start-game'))
async def start_game(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    room_members = await RoomDB.get_list_members(room_number)
    task = get_task(task_id=room_number)
    keyboard = {
        "Изменить время 🕘": f"room_change-game-dt_{room_number}",
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
                '<b>Для запуска игры требуется минимум 3 участника игры</b>'
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
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    
    message_text = (
        '"Хо-хо-хо! 🎅\n\n'
        'Для того, что-бы назначить время рассылки, '
        'отправь сообщение в формате\n'
        '<b>yyyy, mm, dd, h, m</b> - <b>год, месяц, день, час, минуты</b>\n\n'
        '<b>Пример: 2022,12,1,12,00</b>'
    )
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


async def pass_(message):
    await message.answer('test')


@dp.message_handler(state=StartGame.waiting_for_datetime)
async def process_waiting_datetime(message: types.Message, state: FSMContext):
    data = await state.get_data()
    room_number = data['room_number']
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}"
        }
    )
    match = re.fullmatch(r'\d{4},\d{1,2},\d{1,2},\d{1,2},\d{1,2}',
                         message.text)
    
    if match:
        date = datetime(*list(map(int, message.text.split(','))))
        
        if date > datetime.now():
            task = get_task(task_id=room_number)
            if task:
                task.remove()
            
            add_task(
                task_func=send_result_of_game,
                date_time=date,
                task_id=room_number,
                room_number=room_number
            )
            await RoomDB.update(
                room_number,
                started_at=datetime.now(),
                closed_at=None, is_closed=False
            )
            await message.answer(
                'Дата рассылки установлена на'
                f' {date.strftime("%Y-%b-%d, %H:%M:%S")}',
                reply_markup=keyboard_inline
            )
        else:
            await message.answer(
                'Вы указали прошедшую дату. Попробуте снова и укажите '
                'правильную дату для жеребьевки.',
                reply_markup=keyboard_inline
            )
    
    await state.finish()
