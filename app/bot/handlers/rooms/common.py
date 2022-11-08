import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.formatters import profile_information_formatter
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database import game_result_db, room_db
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
        
        message_text = (
            "<b>Игра завершена!</b>\n\n"
            "Вы стали Тайным Сантой для:\n"
            f"{user_information}\n"
            "Ты можешь написать сообщение своему Тайному Санте,"
            "или отправить сообщение своему получателю.\n\n"
            "<b>Учти, что в сутки можно отправлять не более 3х сообщений.</b>"
        )
        
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
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
        
        text_control_room = (
            f'<b>Управление комнатой {room.name}'
            f' ({room.number})</b>'
        )
        text_control_room_scheduler = (
            "<b>🕓 Игра в текущей комнате запущена на "
            f"{scheduler_task.next_run_time.strftime('%Y-%b-%d')}</b>\n\n"
        )
        
        if scheduler_task:
            scheduler_text = text_control_room_scheduler
            message_text = scheduler_text + text_control_room
        else:
            message_text = text_control_room
        
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )
    
    @dp.callback_query_handler(Text(startswith='room_member-list'))
    async def members_list(callback: types.CallbackQuery):
        room_number = get_room_number(callback)
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
        
        message_text = (
            'Список участников комнаты: '
            f'{room.name} ({room_number}):\n\n{member_str}'
        )
        
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
