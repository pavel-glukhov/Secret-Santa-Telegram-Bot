from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types

from app import dispatcher as dp, bot
from app.handlers.profiles import edit_profile
from app.handlers.rooms import delete_room
from app.keyborads.common import create_common_keyboards, check_user_rooms


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
        await delete_room(callback.message, room_number)


# TODO потом переделать под callback
@dp.callback_query_handler(text="about_game")
async def callbacks_num(call: types.CallbackQuery):
    if call.data == "about_game":
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.from_user.id, 'Нажата кнопка об игре!')
