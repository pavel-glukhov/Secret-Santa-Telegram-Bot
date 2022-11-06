import logging
import re
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database import room_db
from app.store.scheduler.operations import add_task, get_task
from app.bot.handlers.operations import get_room_number
from app.bot.messages.result_mailing import send_result_of_game

logger = logging.getLogger(__name__)


class StartGame(StatesGroup):
    waiting_for_datetime = State()


@dp.callback_query_handler(Text(startswith='room_start-game'))
async def start_game(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    room_members = await room_db().get_list_members(room_number)
    task = get_task(task_id=room_number)
    keyboard = {}
    
    if len(list(room_members)) >= 3:
        keyboard.update({"Изменить время 👋": f"room_change-game-dt_{room_number}"})
    keyboard.update({"Вернуться назад ◀️": f"room_menu_{room_number}"})
    
    keyboard_inline = generate_inline_keyboard(keyboard)
    if task:
        await callback.message.edit_text(
            f'<b>Рассылка будет выполнена:</b> {task.next_run_time.strftime("%b-%d-%Y %H:%M")}',
            reply_markup=keyboard_inline
        )
    else:
        await callback.message.edit_text(
            '<b>Время не назначено<b>\n\n',
            '<b>Для запуска игры требуется минимум 3 участника игры</b>',
            reply_markup=keyboard_inline
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
    
    await callback.message.edit_text(
        '"Хо-хо-хо! 🎅\n\n'
        'Для того, что-бы назначить время рассылки, отправь сообщение в формате\n'
        '*yyyy, mm, dd, h, m* - *год, месяц, день, час, минуты*\n\n'
        '*Пример: 2022,12,1,12,00*'
        ,
        reply_markup=keyboard_inline
    )


async def pass_(message):
    await message.answer('test')


# TODO loging
# TODO Добавить календарь и рандомный выбор времени для рассылки
# TODO если дата меньше, вывести ошибку
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
        date = list(map(int, message.text.split(',')))
        task = get_task(task_id=room_number)
        if task:
            task.remove()
        
        add_task(task_func=send_result_of_game,
                 date_time=datetime(*date),
                 task_id=room_number,
                 room_number=room_number
                 )
        await message.answer(
            'Дата рассылки установлена на'
            f' {datetime(*date).strftime("%Y-%b-%d, %H:%M:%S")}',
            reply_markup=keyboard_inline
        )
    
    await state.finish()
