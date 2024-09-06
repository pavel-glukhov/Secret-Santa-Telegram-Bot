import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session

from app.bot.handlers.formatters import profile_information_formatter
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.game_result import GameResultRepo
from app.store.database.queries.rooms import RoomRepo
from app.store.scheduler.operations import get_task

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_menu'))
async def my_room(callback: types.CallbackQuery, session: Session):
    room_number = get_room_number(callback)
    user_id = callback.message.chat.id
    
    room_repo = RoomRepo(session)
    room = await room_repo.get(room_number)
    is_room_owner = await room_repo.is_owner(user_id=user_id, room_number=room_number)
    
    if room.is_closed:
        await _room_is_closed(callback, room.number, user_id, session)
        return
    
    scheduler_task = get_task(room_number)
    keyboard_dict = _generate_keyboard_dict(room_number, is_room_owner, scheduler_task)
    
    message_text = _generate_message_text(room, scheduler_task)
    
    await callback.message.edit_text(text=message_text, reply_markup=generate_inline_keyboard(keyboard_dict))


def _generate_keyboard_dict(room_number: int, is_room_owner: bool, scheduler_task) -> dict:
    is_not_owner_keyboard = {
        'Ваши желания 🎁': f'room_show-wish_{room_number}',
        'Выйти из комнаты 🚪': f'room_exit_{room_number}',
        'Вернуться назад ◀️': 'root_menu',
    }
    
    if is_room_owner:
        start_game_button_name = 'Игра запущена ✅' if scheduler_task else 'Начать игру 🎲'
        is_not_owner_keyboard.pop('Выйти из комнаты 🚪')
        
        owner_keyboard = {
            start_game_button_name: f'room_start-game_{room_number}',
            'Список участников 👥': f'room_member-list_{room_number}',
            'Настройки ⚒': f'room_config_{room_number}'
        }
        owner_keyboard.update(is_not_owner_keyboard)
        return owner_keyboard
    return is_not_owner_keyboard


def _generate_message_text(room, scheduler_task) -> str:
    text_control_room = (
        f'<b>Управление комнатой {room.name}'
        f' ({room.number})</b>\n\n'
        f'<b>Бюджет</b>: {room.budget}\n\n'
    )
    
    if scheduler_task:
        next_time_run = scheduler_task.next_run_time.strftime("%Y-%b-%d")
        text_control_room += (
            '<b>🕓 Игра в текущей комнате запущена на '
            f'{next_time_run}</b>\n\n'
        )
    else:
        text_control_room += '<b>Время жеребьёвки ещё не назначено.</b>'
    
    return text_control_room


async def _room_is_closed(callback: types.CallbackQuery, room_number: int, user_id: int, session: Session) -> None:
    game_result_repo = GameResultRepo(session)
    room_repo = RoomRepo(session)
    
    game_results = await game_result_repo.get_room_id_count(room_id=room_number)
    room_owner = await room_repo.is_owner(user_id=user_id, room_number=room_number)
    
    if game_results <= 0:
        message_text, keyboard_dict = _generate_inactive_room_response(room_number, room_owner)
    else:
        recipient = await game_result_repo.get_recipient(room_id=room_number, user_id=user_id)
        message_text, keyboard_dict = _generate_active_room_response(room_number, recipient)
    
    await callback.message.edit_text(text=message_text, reply_markup=generate_inline_keyboard(keyboard_dict))


def _generate_inactive_room_response(room_number: int, room_owner: bool) -> tuple[str, dict]:
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
        message_text += (
            '\nДля активации комнаты повторно, нажмите на '
            '<b>Активировать комнату</b>, пригласите больше людей '
            'и назначьте новое время жеребьевки.'
        )
    
    return message_text, keyboard_dict


def _generate_active_room_response(room_number: int, recipient) -> tuple[str, dict]:
    keyboard_dict = {
        'Связаться с Сантой': f'room_closed-con-san_{room_number}',
        'Связаться с получателем': f'room_closed-con-rec_{room_number}',
        'Вернуться в меню': 'root_menu'
    }
    
    user_information = profile_information_formatter(recipient)
    
    message_text = (
        '<b>Игра в вашей комнате завершена!</b>\n\n'
        'Вы стали Тайным Сантой для:\n'
        f'{user_information}\n'
        'Ты можешь написать сообщение своему Тайному Санте, '
        'или отправить сообщение своему получателю.\n'
    )
    
    return message_text, keyboard_dict
