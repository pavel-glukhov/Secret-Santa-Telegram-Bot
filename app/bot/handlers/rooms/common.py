import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers import texts
from app.bot.handlers.formatters import profile_information_formatter
from app.store.database import room_db, game_result_db
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.handlers.operations import get_room_number
from app.store.scheduler.operations import get_task

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_menu'))
async def my_room(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    scheduler_task = get_task(room_number)
    room = await room_db().get(room_number)
    user_id = callback.message.chat.id
    is_room_owner = await room_db().is_owner(user_id=user_id,
                                             room_number=room_number)
    
    if room.is_closed:
        
        keyboard_dict = {
            "Связаться с Сантой": f"1",  # TODO добавить коллбак
            "Отправить сообщение получателю": f"1",  # TODO добавить коллбак
            "Вернуться в меню": "root_menu"
        }
        recipient = await game_result_db().get_recipient(room_id=room_number,
                                                         user_id=user_id)
        keyboard_inline = generate_inline_keyboard(keyboard_dict)
        user_information = profile_information_formatter(recipient)
        await callback.message.edit_text(
            texts.GENERAL_COMPLETED_GAME.format(
                user_information,
            ),
            reply_markup=keyboard_inline
        )
    
    else:
        keyboard_dict = {
            "Ваши желания 🎁": f"room_show-wish_{room_number}",
            "Выйти из комнаты 🚪": f"room_exit_{room_number}"
        }
        
        if is_room_owner:
            if not get_task(room_number):
                start_game_button_name = "Начать игру 🎲"
            else:
                start_game_button_name = 'Игра запущена ✅'
            
            keyboard_dict.update(
                {
                    start_game_button_name: f"room_start-game_{room_number}",
                    "Список участников 👥": f"room_member-list_{room_number}",
                    "Настройки ⚒": f"room_config_{room_number}"
                }
            )
        keyboard_dict.update(
            {
                "Вернуться назад ◀️": "root_menu",
            }
        )
        keyboard_inline = generate_inline_keyboard(keyboard_dict)
        
        menu_text_message = texts.CONTROL_ROOM.format(
            room.name, room.number,
        )
        if scheduler_task:
            scheduler_text = texts.CONTROL_ROOM_SCHEDULER.format(
                scheduler_task.next_run_time.strftime('%Y-%b-%d'),
            )
            message_text = scheduler_text + menu_text_message
        else:
            message_text = menu_text_message
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard_inline
        )
    
    @dp.callback_query_handler(Text(startswith='room_member-list'))
    async def members_list(callback: types.CallbackQuery):
        room_number = get_room_number(callback)
        message = callback.message
        keyboard_inline = generate_inline_keyboard(
            {
                "Вернуться назад ◀️": f"room_menu_{room_number}"
            }
        )
        room = await room_db().get(room_number)
        members = await room.members
        member_str = ''
        
        for number, member in enumerate(members):
            member_str += f'{number}) @{member.username}\n'
        
        await message.edit_text(
            texts.LIST_MEMBERS.format(room.name,
                                      room_number,
                                      member_str),
            reply_markup=keyboard_inline
        )
