from aiogram.dispatcher.filters.state import State, StatesGroup


class DeleteRoom(StatesGroup):
    waiting_conformation = State()


class CreateRoom(StatesGroup):
    waiting_for_room_name = State()
    waiting_for_room_budget = State()
    waiting_for_room_wishes = State()


class ChangeOwner(StatesGroup):
    waiting_for_owner_name = State()


class JoinRoom(StatesGroup):
    waiting_for_room_number = State()
    waiting_for_wishes = State()


class ChangeRoomName(StatesGroup):
    waiting_for_room_name = State()


class ChangeBudget(StatesGroup):
    waiting_for_budget = State()
