from aiogram import types

from app.database.config import async_session
from app.database.operations import RoomDB


async def check_user_rooms(message: types.Message) -> list:
    user_id = message.chat.id
    async with async_session() as db_session:
        async with db_session.begin():
            rooms = await RoomDB(db_session).get_joined_in_rooms(user_id)

    return rooms


async def create_common_keyboards(rooms: list) -> types.ReplyKeyboardMarkup:
    users_list_rooms = []
    if rooms:
        for room in rooms:
            users_list_rooms.append(
                f'Ваша комната: {room.name} ({room.number})'
            )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_room = types.KeyboardButton(text="Создать комнату 🔨")
    join_room = types.KeyboardButton(text="Войти в комнату 🏠")
    about = types.KeyboardButton(text="Об игре ℹ️")
    user_profile = types.KeyboardButton(text="Мой профиль 👤")

    keyboard.add(join_room, create_room)
    if users_list_rooms:
        for room in users_list_rooms:
            keyboard.add(room)
    keyboard.add(user_profile)
    keyboard.add(about)
    return keyboard
