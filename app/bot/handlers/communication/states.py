from aiogram.dispatcher.filters.state import StatesGroup, State


class MessageToSanta(StatesGroup):
    waiting_message = State()


class MessageToRecipient(StatesGroup):
    waiting_message = State()
