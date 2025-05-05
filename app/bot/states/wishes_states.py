from aiogram.fsm.state import State, StatesGroup


class ChangeWish(StatesGroup):
    waiting_for_wishes = State()
