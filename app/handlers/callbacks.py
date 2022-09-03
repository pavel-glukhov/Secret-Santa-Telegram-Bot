from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app import dispatcher as dp
from app.handlers.common import about_game, root_menu
from app.handlers.profiles.common import edit_profile, my_profile
from app.handlers.rooms.change_owner import change_room_owner
from app.handlers.rooms.common import members_list, my_room
from app.handlers.rooms.config_room import configuration_room
from app.handlers.rooms.create_room import create_room
from app.handlers.rooms.delete_room import delete_room
from app.handlers.rooms.subscribe_room import join_room
from app.handlers.rooms.unsubscribe_room import left_room
from app.handlers.rooms.update_room import update_room_name
from app.handlers.wishes.common import show_wishes, update_wishes


@dp.callback_query_handler(text_contains="cancel", state='*')
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await state.reset_state()
    await message.answer('Действие отменено')
    await root_menu(message)


@dp.callback_query_handler(Text(startswith="root"))
async def main(callback: types.CallbackQuery):
    if callback.data == 'root_menu':
        await root_menu(callback.message, True)


@dp.callback_query_handler(Text(startswith="menu"))
async def main_menu(callback: types.CallbackQuery):
    if callback.data == 'menu_create_new_room':
        await create_room(callback.message)
    if callback.data == 'menu_join_room':
        await join_room(callback.message)
    if callback.data == 'menu_user_profile':
        await my_profile(callback.message)
    if callback.data == 'menu_about_game':
        await about_game(callback.message)


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

    if operation == 'menu':
        await my_room(callback.message, room_number)
    if operation == 'delete':
        await delete_room(callback.message, room_number)
    if operation == 'member-list':
        await members_list(callback.message, room_number)
    if operation == 'exit':
        await left_room(callback.message, room_number)
    if operation == 'change-name':
        await update_room_name(callback.message, room_number)
    if operation == 'show-wish':
        await show_wishes(callback.message, room_number)
    if operation == 'change-wish':
        await update_wishes(callback.message, room_number)
    if operation == 'change-owner':
        await change_room_owner(callback.message, room_number)
    if operation == 'config':
        await configuration_room(callback.message, room_number)
