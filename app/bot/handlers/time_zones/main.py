import logging

import pycountry
import pytz
from aiogram import filters, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.handlers.pagination import Pagination
from app.bot.states.time_zones import TimeZoneStates
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.users import UserRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='change_time_zone'))
async def get_letter(callback: types.CallbackQuery):
    await TimeZoneStates.selecting_letter.set()
    state = dp.get_current().current_state()
    room_number = get_room_number(callback)
    
    if room_number:
        await state.update_data(room_number=room_number)
    
    message_text = (
        "Для смены часового пояса, выберите букву,"
        " на которую начинается страна:"
    )
    
    await callback.message.edit_text(
        message_text,
        reply_markup=_get_letter_keyboard())
    await TimeZoneStates.next()


def _get_letter_keyboard():
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    keyboard_markup = InlineKeyboardMarkup(row_width=5)
    for letter in alphabet:
        button = InlineKeyboardButton(text=letter,
                                      callback_data=f'selected_letter:{letter}')
        keyboard_markup.insert(button)
    return keyboard_markup


@dp.callback_query_handler(Text(startswith='selected_letter'),
                           state=TimeZoneStates.selecting_country)
async def process_letter_callback(callback: types.CallbackQuery):
    letter = callback.data.split(':')[-1]
    message_text = "Выберите страну:"
    await callback.message.edit_text(message_text,
                                     reply_markup=get_country_keyboard(
                                         letter))
    await TimeZoneStates.next()


@dp.callback_query_handler(Text(startswith='selected_country'),
                           state=TimeZoneStates.selecting_timezone)
async def process_country_callback(callback: types.CallbackQuery):
    country_code = callback.data.split(':')[-1]
    message_text = 'Выберите таймзону:'
    await callback.message.edit_text(text=message_text,
                                     reply_markup=get_timezone_keyboard(
                                         country_code))
    await TimeZoneStates.next()


@dp.callback_query_handler(Text(startswith='selected_timezone'),
                           state=TimeZoneStates.confirmation)
async def process_timezone_callback(callback: types.CallbackQuery,
                                    state: FSMContext):
    timezone = callback.data.split(':')[-1]
    state_data = await state.get_data()
    room_number = state_data.get('room_number')
    
    if room_number:
        callback_query = f"room_start-game_{room_number}"
    else:
        callback_query = "profile_edit"
    
    message_text = f"Выбран часовой пояс {timezone}"
    keyboard = {
        "Вернуться назад ◀️": callback_query
    }
    keyboard_inline = generate_inline_keyboard(keyboard)
    await UserRepo().update_user(user_id=callback.message.chat.id,
                                 timezone=timezone)
    await callback.message.edit_text(message_text, reply_markup=keyboard_inline)
    await state.finish()


def get_country_keyboard(letter, page=1):
    countries = [country for country in pycountry.countries if
                 country.name.startswith(letter)]
    return Pagination(countries, 5,
                      callback_next_prefix=f'next_country:{letter}',
                      callback_back_prefix=f'prev_country:{letter}',
                      callback_prefix='selected_country',
                      keyboard_name_or_method='name',
                      callback_name_or_method='alpha_2'
                      ).inline_pagination(page)
    

@dp.callback_query_handler(filters.Regexp(r'prev_country:[A-Z]:\d+'),
                           state=TimeZoneStates.selecting_timezone)
async def process_prev_country_callback(callback: types.CallbackQuery):
    data = callback.data.split(':')
    letter = data[1]
    page = int(data[2])
    message_text = 'Страна'
    await callback.message.edit_text(message_text,
                                     reply_markup=get_country_keyboard(
                                         letter, page - 1))


@dp.callback_query_handler(filters.Regexp(r'next_country:[A-Z]:\d+'),
                           state=TimeZoneStates.selecting_timezone)
async def process_next_country_callback(callback: types.CallbackQuery):
    data = callback.data.split(':')
    letter = data[1]
    page = int(data[2])
    message_text = 'Страна'
    await callback.message.edit_text(message_text,
                                     reply_markup=get_country_keyboard(
                                         letter, page + 1))


def get_timezone_keyboard(country_code, page=1):
    timezones = pytz.country_timezones.get(country_code, [])
    return Pagination(timezones, 5,
                      callback_next_prefix=f'next_timezone:{country_code}',
                      callback_back_prefix=f'prev_timezone:{country_code}',
                      callback_prefix='selected_timezone',
                      ).inline_pagination(page)


@dp.callback_query_handler(filters.Regexp(r'prev_timezone:[A-Z]{2}:\d+'),
                           state=TimeZoneStates.confirmation)
async def process_prev_timezone_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split(':')
    country_code = data[1]
    page = int(data[2])
    await callback_query.message.edit_text('Таймзона',
                                           reply_markup=get_timezone_keyboard(
                                               country_code, page - 1))


@dp.callback_query_handler(filters.Regexp(r'next_timezone:[A-Z]{2}:\d+'),
                           state=TimeZoneStates.confirmation)
async def process_next_timezone_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split(':')
    country_code = data[1]
    page = int(data[2])
    await callback_query.message.edit_text('Таймзона',
                                           reply_markup=get_timezone_keyboard(
                                               country_code, page + 1))
