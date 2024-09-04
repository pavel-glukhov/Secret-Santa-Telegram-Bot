import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.profiles import ChangeUserName
from app.store.database.queries.users import UserRepo

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'profile_edit_name')
async def change_username(callback: types.CallbackQuery, state: FSMContext):
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    
    message_text = (
        'Хохохо, пора указать твои данные для Санты 🎅\n'
        'Учти, что оно будет использоваться для отправки подарка Сантой.\n\n'
        '<b>Сначала напиши свое имя</b>\n\n'
    )
    initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeUserName.waiting_for_first_name)


@router.message(ChangeUserName.waiting_for_first_name)
async def process_changing_first_name(message: types.Message,
                                      state: FSMContext):
    first_name = message.text
    await state.update_data(first_name=first_name)
    
    await message.delete()
    
    state_data = await state.get_data()
    bot_message = state_data['bot_message_id']
    
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    
    message_text = '<b>Теперь укажи свою фамилию</b>\n\n'
    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.set_state(ChangeUserName.waiting_for_last_name)


@router.message(ChangeUserName.waiting_for_last_name)
async def process_changing_last_name(message: types.Message,
                                     state: FSMContext, session: Session):
    state_data = await state.get_data()
    first_name = state_data.get('first_name')
    last_name = message.text
    user_id = message.chat.id
    bot_message = state_data.get('bot_message_id')
    
    await message.delete()
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "profile_edit",
        }
    )
    await UserRepo(session).update_user(user_id,
                                        first_name=first_name,
                                        last_name=last_name)
    logger.info(f'The user [{user_id}] updated fist and last name.')
    
    message_text = 'Имя и фамилия изменены.'
    
    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.clear()
