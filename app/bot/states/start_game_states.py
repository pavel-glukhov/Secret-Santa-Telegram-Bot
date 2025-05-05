from aiogram.fsm.state import State, StatesGroup


class DateTimePicker(StatesGroup):
    picking_date = State()
    picking_time = State()