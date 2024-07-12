from aiogram.dispatcher.filters.state import State, StatesGroup


class MessageToSanta(StatesGroup):
    waiting_message = State()


class MessageToRecipient(StatesGroup):
    waiting_message = State()
