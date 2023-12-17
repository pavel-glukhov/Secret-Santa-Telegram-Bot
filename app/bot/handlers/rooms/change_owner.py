import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number, delete_user_message
from app.bot.handlers.rooms.states import ChangeOwner
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.models import User
from app.store.database.queries.rooms import RoomDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_change-owner'))
async def change_room_owner(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    await ChangeOwner.waiting_for_owner_name.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        'Хочешь поменять владельца комнаты?\n'
        'Новый владелец комнаты должен являться ее участником. '
        '<b>Учти, что ты потеряешь контроль за комнатой.</b>\n\n'
        '<b>Для смены владельца, напиши его ник.</b>\n'
    )
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.message_handler(state=ChangeOwner.waiting_for_owner_name)
async def process_changing_owner(message: types.Message, state: FSMContext):
    state_data = await dp.current_state().get_data()
    room_number = state_data['room_number']
    previous_owner = message.chat.id
    new_owner = message.text
    last_message = state_data['last_message']
    await delete_user_message(message.from_user.id, message.message_id)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}",
        }
    )

    owner: User = await RoomDB.change_owner(new_owner, room_number)
    
    if owner:
        message_text = (
            '"Хо-хо-хо! 🎅\n\n'
            f'Я сменил владельца, теперь это <b>{new_owner}</b>'
        )
        
        await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        await state.finish()
        logger.info(f'The owner [{previous_owner}] of room '
                    f'[{room_number}] has been changed to [{owner.user_id}]')
    else:
        
        message_text = 'Такой участник не найден.'
        
        await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        await state.finish()
