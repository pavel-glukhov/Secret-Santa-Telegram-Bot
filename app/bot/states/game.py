from aiogram.fsm.state import State, StatesGroup


class StartGame(StatesGroup):
    waiting_for_datetime = State()