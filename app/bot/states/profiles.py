from aiogram.dispatcher.filters.state import State, StatesGroup


class ChangeAddress(StatesGroup):
    waiting_for_address_information = State()


class ChangeUserName(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()


class ChangePhoneNuber(StatesGroup):
    waiting_for_phone_number = State()


class DeleteUserInformation(StatesGroup):
    waiting_for_conformation = State()
