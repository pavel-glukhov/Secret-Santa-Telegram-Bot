from aiogram.dispatcher.filters.state import State, StatesGroup


class ChangeWish(StatesGroup):
    waiting_for_wishes = State()