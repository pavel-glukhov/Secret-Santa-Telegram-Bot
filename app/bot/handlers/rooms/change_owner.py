import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.rooms import ChangeOwner
from app.config import load_config
from app.store.queries.rooms import RoomRepo
from app.store.queries.users import UserRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_change-owner'))
async def change_room_owner(callback: types.CallbackQuery, state: FSMContext):
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)
    
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        'Хочешь поменять владельца комнаты?\n'
        'Новый владелец комнаты должен являться ее участником.\n'
        '<b>Учти, что ты потеряешь контроль за комнатой.</b>\n\n'
        '<b>Для смены владельца, напиши его ник.</b>\n'
    )
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeOwner.waiting_for_owner_name)


@router.message(ChangeOwner.waiting_for_owner_name)
async def process_changing_owner(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    previous_owner = message.chat.id
    new_owner = message.text
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}",
        }
    )
    user = await UserRepo().get_user_or_none(new_owner)
    
    if user:
        count_rooms = await RoomRepo().get_count_user_rooms(user.user_id)
        if count_rooms < load_config().room.user_rooms_count:
            await RoomRepo().change_owner(new_owner, room_number)
            
            message_text = (
                'Хо-хо-хо! 🎅\n\n'
                f'Я сменил владельца, теперь это <b>{new_owner}</b>'
            )
            
            await bot_message.edit_text(
                text=message_text,
                reply_markup=keyboard_inline,
            )
            await state.clear()
            logger.info(f'The owner [{previous_owner}] of room '
                        f'[{room_number}] has been changed to [{user.user_id}]')
        else:
            message_text = ('Данный участник не может '
                            'быть назначен владельцем комнаты.')
            
            await bot_message.edit_text(
                text=message_text,
                reply_markup=keyboard_inline,
            )
            await state.clear()
    else:
        message_text = 'Такой участник не найден.'
        
        await bot_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        await state.clear()
