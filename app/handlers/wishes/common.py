from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp, bot
from app.database import wish_db, room_db
from app.keyborads.common import (
    create_common_keyboards,
)


class ChangeWish(StatesGroup):
    waiting_for_wishes = State()


async def show_wishes(message: types.Message,
                      room_number: int):
    change_wish = types.InlineKeyboardButton(
        text="Изменить желание ✒️",
        callback_data=f"room_change-wish_{room_number}"
    )
    keyboard_inline = types.InlineKeyboardMarkup().add(change_wish)
    user_id = message.chat.id
    wishes = await wish_db().get_wishes(user_id, room_number)

    await message.edit_text('Ваши тайные желания 🙊: \n'
                            f'{wishes.wish}\n',
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=keyboard_inline)


async def update_wishes(message: types.Message,
                        room_number: int):
    await ChangeWish.waiting_for_wishes.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    await message.edit_text(
        '*Напиши новое желание:*\n\n'
        'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


async def process_updating_wishes(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    keyboard = await create_common_keyboards(message)
    async with state.proxy() as data:
        wish = message.text
        room_number = data['room_number']

    await wish_db().update_or_create(
        wish,
        user_id,
        room_number
    )
    room = await room_db().get_room(room_number)
    await state.finish()
    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=message.message_id)
    await message.answer(
        f'Ваши желания в комнате *{room.name}* изменены на:\n\n'
        f'{wish}\n\n'
        f'Санта обязательно учтет ваши пожелания! 🎅',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )
