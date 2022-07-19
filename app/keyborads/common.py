from aiogram import types

from app.database.operations import RoomDB


async def create_common_keyboards(message) -> types.ReplyKeyboardMarkup:
    user_id = message.chat.id
    rooms = await RoomDB().get_joined_in_rooms(user_id)
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
