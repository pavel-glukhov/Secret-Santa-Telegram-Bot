from aiogram import types
from aiogram.dispatcher.filters import Text

from app import bot
from app import dispatcher as dp
from app.handlers.profiles.common import edit_profile
from app.handlers.rooms.change_owner import change_room_owner
from app.handlers.rooms.common import members_list
from app.handlers.rooms.delete_room import delete_room
from app.handlers.rooms.unsubscribe_room import left_room
from app.handlers.rooms.update_room import update_room_name
from app.handlers.wishes.common import update_wishes


@dp.callback_query_handler(Text(startswith="profile_edit"))
async def edit_user_profile(callback: types.CallbackQuery):
    if callback.data == 'profile_edit':
        await edit_profile(callback.message)

    if callback.data == 'profile_edit_name':
        pass

    if callback.data == 'profile_edit_address':
        pass

    if callback.data == 'profile_edit_number':
        pass

    if callback.data == 'profile_edit_delete_all':
        pass


@dp.callback_query_handler(Text(startswith="room_"))
async def room_operations(callback: types.CallbackQuery):
    command, operation, room_number = callback.data.split('_')
    if operation == 'delete':
        await delete_room(callback.message,
                          room_number=room_number)

    if operation == 'member-list':
        await members_list(callback.message,
                           room_number=room_number)

    if operation == 'exit':
        await left_room(callback.message,
                        room_number=room_number)

    if operation == 'change-name':
        await update_room_name(callback.message,
                               room_number=room_number)
    if operation == 'change-wish':
        await update_wishes(callback.message,
                            room_number=room_number)
    if operation == 'change-owner':
        await change_room_owner(callback.message,
                                room_number=room_number)
