import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import delete_user_message
from app.bot.handlers.profiles.states import ChangeUserName
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.users import UserDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(equals='profile_edit_name'))
async def change_username(callback: types.CallbackQuery):
    await ChangeUserName.waiting_for_first_name.set()
    state = dp.get_current().current_state()

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    
    message_text = (
        'Хохохо, пора указать твои данные для Санты 🎅\n'
        'Учти, что оно будет использоваться для отправки подарка Сантой.\n\n'
        '<b>Сначала напиши свое имя</b>\n\n'
    )
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangeUserName.waiting_for_first_name)
async def process_changing_first_name(message: types.Message,
                                      state: FSMContext):
    first_name = message.text
    state_data = await state.get_data()
    last_message = state_data['last_message']
    await state.update_data(first_name=first_name)
    await delete_user_message(message.from_user.id,
                              message.message_id)
    
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = '<b>Теперь укажи свою фамилию</b>\n\n'
    
    await ChangeUserName.next()
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangeUserName.waiting_for_last_name)
async def process_changing_last_name(message: types.Message,
                                     state: FSMContext):
    state_data = await state.get_data()
    last_message = state_data['last_message']
    first_name = state_data['first_name']
    last_name = message.text
    user_id = message.chat.id

    await delete_user_message(message.from_user.id,
                              message.message_id)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "menu_user_profile",
        }
    )
    await UserDB.update_user(user_id,
                             first_name=first_name,
                             last_name=last_name)
    logger.info(f'The user [{user_id}] updated fist and last name.')
    message_text = 'Имя и фамилия изменены.'
    
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.finish()
