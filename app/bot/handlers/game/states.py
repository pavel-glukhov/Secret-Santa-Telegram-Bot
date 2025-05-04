from aiogram.fsm.state import StatesGroup, State


class DateTimePicker(StatesGroup):
    picking_date = State()
    picking_time = State()