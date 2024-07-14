import logging

from aiogram import F, Router, types
from app.bot.handlers.formatters import profile_information_formatter
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.game_result import GameResultRepo
from app.store.queries.rooms import RoomRepo
from app.store.scheduler.operations import get_task

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith('room_menu'))
async def my_room(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    scheduler_task = get_task(room_number)
    room = await RoomRepo().get(room_number)
    user_id = callback.message.chat.id
    is_room_owner = await RoomRepo().is_owner(user_id=user_id,
                                              room_number=room_number)
    
    if room.is_closed:
        await _room_is_closed(callback, room.number, user_id)
    
    else:
        keyboard_dict = {
            'Ваши желания 🎁': f'room_show-wish_{room_number}',
            'Выйти из комнаты 🚪': f'room_exit_{room_number}'
        }
        
        if is_room_owner:
            if not get_task(room_number):
                start_game_button_name = 'Начать игру 🎲'
            else:
                start_game_button_name = 'Игра запущена ✅'
            del keyboard_dict['Выйти из комнаты 🚪']
            keyboard_dict.update(
                {
                    start_game_button_name: f'room_start-game_{room_number}',
                    'Список участников 👥': f'room_member-list_{room_number}',
                    'Настройки ⚒': f'room_config_{room_number}'
                }
            )
        keyboard_dict.update(
            {
                'Вернуться назад ◀️': 'root_menu',
            }
        )
        keyboard_inline = generate_inline_keyboard(keyboard_dict)
        
        text_control_room = (
            f'<b>Управление комнатой {room.name}'
            f' ({room.number})</b>\n\n'
            f'<b>Бюджет</b>: {room.budget}\n\n'
        )
        text_control_room_not_scheduler = (
            '<b>Время жеребьёвки ещё не назначено.</b>'
        )
        if scheduler_task:
            next_time_run = scheduler_task.next_run_time.strftime("%Y-%b-%d")
            text_control_room_scheduler = (
                '<b>🕓 Игра в текущей комнате запущена на '
                f'{next_time_run}</b>\n\n'
            )
            
            message_text = text_control_room + text_control_room_scheduler
        else:
            message_text = text_control_room + text_control_room_not_scheduler
        
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )


async def _room_is_closed(callback: types.CallbackQuery,
                          room_number: int, user_id: int) -> None:
    game_results = await GameResultRepo().get_all_recipients(
        room_id=room_number)
    room_owner = await RoomRepo().is_owner(user_id=user_id,
                                           room_number=room_number)
    if not game_results:
        keyboard_dict = {
            'Активировать комнату ✅': f'room_activate_{room_number}',
            'Настройки ⚒': f'room_config_{room_number}',
            'Вернуться в меню ◀️': 'root_menu',
        }
        
        if not room_owner:
            del keyboard_dict['Активировать комнату ✅']
            del keyboard_dict['Настройки ⚒']
        
        message_text = (
            f'<b>Игра в комнате {room_number} завершена!</b>\n\n'
            'К сожалению, количество игроков оказалось недостаточным '
            'для полноценной жеребьевки.\n'
        
        )
        if room_owner:
            additional_text = (
                '\nДля активации комнаты повторно, нажмите на '
                '<b>Активировать комнату</b>, пригласите больше людей '
                'и назначьте новое время жеребьевки.'
            )
            message_text = message_text + additional_text
    else:
        keyboard_dict = {
            'Связаться с Сантой': f'room_closed-con-san_{room_number}',
            'Связаться с получателем': f'room_closed-con-rec_{room_number}',
            'Вернуться в меню': 'root_menu'
        }
        recipient = await GameResultRepo().get_recipient(room_id=room_number,
                                                         user_id=user_id)
        user_information = profile_information_formatter(recipient)
        
        message_text = (
            '<b>Игра в вашей комнате завершена!</b>\n\n'
            'Вы стали Тайным Сантой для:\n'
            f'{user_information}\n'
            'Ты можешь написать сообщение своему Тайному Санте,'
            'или отправить сообщение своему получателю.\n'
        )
    
    keyboard_inline = generate_inline_keyboard(keyboard_dict)
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
