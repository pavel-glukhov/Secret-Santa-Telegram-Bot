import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import delete_user_message
from app.bot.states.rooms import CreateRoom
from app.bot.keyborads.common import generate_inline_keyboard
from app.config import load_config
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(equals='menu_create_new_room'))
async def create_room(callback: types.CallbackQuery, ):
    count_user_rooms = await RoomRepo().get_count_user_rooms(
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
    
    await CreateRoom.waiting_for_room_name.set()
    state = dp.get_current().current_state()
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        'Хо-хо-хо! 🎅\n\n'
        'Как ты хочешь назвать свою комнату?\n'
        'Напиши мне ее название и мы пойдем дальше\n\n'
        'Имя комнаты не должно превышать 16 символов.\n'
    )
    
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )


@dp.message_handler(state=CreateRoom.waiting_for_room_name)
async def process_name(message: types.Message, state: FSMContext):
    room_name = message.text
    state_data = await state.get_data()
    last_message = state_data['last_message']
    await state.update_data(room_name=room_name)
    await state.update_data(budget_question_id=message.message_id)
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    await delete_user_message(message.from_user.id, message.message_id)
    
    if not len(room_name) < 17:
        keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
        
        message_text = (
            'Вы ввели слишком длинное имя, '
            'пожалуйста придумайте другое.\n'
            'Имя комнаты не должно превышать 16 символов.\n'
        )
        
        return await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )
    await CreateRoom.next()
    
    message_text = (
        f'Принято! Имя твоей комнаты <b>{room_name}</b>\n\n'
        'А теперь укажи максимальный бюджет '
        'на подарок Тайного Санты.\n'
        'Напиши в чат сумму в любом формате, '
        'например 2000 тенге,'
        '200 рублей или 20$\n\n'
        'Длина сообщения не должна превышать 16 символов.'
    )
    
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message:
                    len(message.text.lower()) > 16,
                    state=CreateRoom.waiting_for_room_budget)
async def process_budget_invalid(message: types.Message):
    state_data = await dp.get_current().current_state().get_data()
    last_message = state_data['last_message']
    await delete_user_message(message.from_user.id, message.message_id)
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    logger.info('long budget message'
                f' command from [{message.from_user.id}] ')
    
    message_text = (
        'Вы введи слишком длинное сообщение для бюджета.\n '
        'Длина сообщения не может быть больше 16 символов\n'
        'Для изменения вашего бюджета, отправьте новое сообщение.\n'
    )
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_budget)
async def process_budget(message: types.Message, state: FSMContext):
    await state.update_data(wishes_question_message_id=message.message_id)
    state_data = await state.get_data()
    last_message = state_data['last_message']
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    room_budget = message.text
    await state.update_data(room_budget=room_budget)
    await delete_user_message(message.from_user.id, message.message_id)
    
    await CreateRoom.next()
    
    message_text = (
        f'Принято! Ваш бюджет будет составлять <b>{room_budget}</b>\n\n'
        'И последний вопрос.\n'
        'Напиши свои пожелания по подарку. '
        'Возможно у тебя есть хобби и '
        'ты хочешь получить что-то особое?\n'
    )
    
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=CreateRoom.waiting_for_room_wishes)
async def process_wishes(message: types.Message, state: FSMContext):
    user_wishes = message.text
    state_data = await state.get_data()
    last_message = state_data['last_message']
    keyboard_inline = generate_inline_keyboard({"Меню ◀️": 'root_menu'})
    await delete_user_message(message.from_user.id, message.message_id)
    room = await RoomRepo().create(user_wish=user_wishes,
                                   owner=message.chat.id,
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
    
    await last_message.edit_text(
        text=message_text,
    )
    message_text = "А пока ты можешь вернуться назад и обновить свой профиль"
    
    await last_message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.finish()
