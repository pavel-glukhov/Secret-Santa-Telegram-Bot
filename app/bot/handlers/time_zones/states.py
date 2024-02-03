from aiogram.dispatcher.filters.state import State, StatesGroup


class TimeZoneStates(StatesGroup):
    selecting_letter = State()
    selecting_country = State()
    selecting_timezone = State()

