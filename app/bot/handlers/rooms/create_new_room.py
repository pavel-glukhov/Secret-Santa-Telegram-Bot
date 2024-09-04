import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.rooms import CreateRoom
from app.config import load_config
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'menu_create_new_room')
async def create_room(callback: types.CallbackQuery, state: FSMContext, session: Session):
    count_user_rooms = await RoomRepo(session).get_count_user_rooms(
        callback.message.chat.id)
    logger.info(count_user_rooms)
    if count_user_rooms >= load_config().room.user_rooms_count:
        keyboard_inline = generate_inline_keyboard(
            {
                "Вернуться назад ◀️": "root_menu",
            }
        )
        message_text = (
            '<b>Новая комната не может быть создана, '
            'т.к. вы достигли лимита.</b>\n\n '
            'Вы можете являться владельцем только 10 комнат.'
        )
        return await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )
    
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        'Хо-хо-хо! 🎅\n\n'
        'Как ты хочешь назвать свою комнату?\n'
        'Напиши мне ее название и мы пойдем дальше\n\n'
        'Имя комнаты не должно превышать 16 символов.\n'
    )
    
    initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(CreateRoom.waiting_for_room_name)


@router.message(CreateRoom.waiting_for_room_name)
async def process_name(message: types.Message, state: FSMContext):
    room_name = message.text
    state_data = await state.get_data()
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    await state.update_data(room_name=room_name)
    await state.update_data(budget_question_id=message.message_id)
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    if not len(room_name) < 17:
        keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
        
        message_text = (
            'Вы ввели слишком длинное имя, '
            'пожалуйста придумайте другое.\n'
            'Имя комнаты не должно превышать 16 символов.\n'
        )
        
        return await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.set_state(CreateRoom.waiting_for_room_budget)
    
    message_text = (
        f'Принято! Имя твоей комнаты <b>{room_name}</b>\n\n'
        'А теперь укажи максимальный бюджет '
        'на подарок Тайного Санты.\n'
        'Напиши в чат сумму в любом формате, '
        'например 2000 тенге,'
        '200 рублей или 20$\n\n'
        'Длина сообщения не должна превышать 16 символов.'
    )
    
    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(lambda message:
                len(message.text.lower()) > 16,
                StateFilter(CreateRoom.waiting_for_room_budget))
async def process_budget_invalid(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    logger.info('long budget message'
                f' command from [{message.from_user.id}] ')
    
    message_text = (
        'Вы введи слишком длинное сообщение для бюджета.\n '
        'Длина сообщения не может быть больше 16 символов\n'
        'Для изменения вашего бюджета, отправьте новое сообщение.\n'
    )
    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(CreateRoom.waiting_for_room_budget)
async def process_budget(message: types.Message, state: FSMContext):
    await state.update_data(wishes_question_message_id=message.message_id)
    state_data = await state.get_data()
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    room_budget = message.text
    await state.update_data(room_budget=room_budget)
    
    await state.set_state(CreateRoom.waiting_for_room_wishes)
    
    message_text = (
        f'Принято! Ваш бюджет будет составлять <b>{room_budget}</b>\n\n'
        'И последний вопрос.\n'
        'Напиши свои пожелания по подарку. '
        'Возможно у тебя есть хобби и '
        'ты хочешь получить что-то особое?\n'
    )
    
    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(CreateRoom.waiting_for_room_wishes)
async def process_wishes(message: types.Message, state: FSMContext, session: Session):
    user_wishes = message.text
    state_data = await state.get_data()
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard({"Меню ◀️": 'root_menu'})
    
    room = await RoomRepo(session).create(user_wish=user_wishes,
                                          owner_id=message.chat.id,
                                          name=state_data['room_name'],
                                          budget=state_data['room_budget'])
    
    logger.info(
        f'The new room "{room.number}" has been created by {message.chat.id}'
    )
    message_text = (
        '"Хо-хо-хо! 🎅\n\n'
        f'Комната <b>"{room.name}"</b> создана.\n'
        f'Держи номер комнаты <b>{room.number}</b>\n'
        f'Этот код нужно сообщить своим друзьям, '
        f'что бы они присоединились '
        f'к твоей игре.\n\n'
    )
    
    await bot_message.edit_text(text=message_text)
    message_text = "А пока ты можешь вернуться назад и обновить свой профиль"
    
    await bot_message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.clear()
