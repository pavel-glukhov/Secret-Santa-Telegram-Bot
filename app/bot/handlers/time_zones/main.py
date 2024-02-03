import logging
from aiogram import types, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pytz
import pycountry
from app.bot import dispatcher as dp

from app.bot.handlers.time_zones.states import TimeZoneStates

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='change_time_zone'))
async def get_letter(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите букву, на которую начинается страна:",
        reply_markup=get_letter_keyboard())
    await TimeZoneStates.selecting_letter.set()
    

def get_letter_keyboard():
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    keyboard_markup = InlineKeyboardMarkup(row_width=5)
    for letter in alphabet:
        button = InlineKeyboardButton(text=letter,
                                      callback_data=f'select_letter:{letter}')
        keyboard_markup.insert(button)
    return keyboard_markup


@dp.callback_query_handler(state=TimeZoneStates.selecting_letter)
async def process_letter_callback(callback: types.CallbackQuery,
                                  state: FSMContext):
    letter = callback.data.split(':')[-1]
    await callback.message.reply("Выберите страну:",
                                 reply_markup=get_country_keyboard(letter))
    await TimeZoneStates.next()


@dp.callback_query_handler(state=TimeZoneStates.selecting_country)
async def process_country_callback(callback: types.CallbackQuery):
    country_code = callback.data.split(':')[-1]
    country = pycountry.countries.get(alpha_2=country_code)
    await callback.message.reply(f"Выбрана страна {country.name}")
    await callback.message.reply("Выберите таймзону:",
                                 reply_markup=get_timezone_keyboard(
                                     country.alpha_2))
    await TimeZoneStates.next()


@dp.callback_query_handler(state=TimeZoneStates.selecting_timezone)
async def process_timezone_callback(callback: types.CallbackQuery):
    timezone = callback.data.split(':')[-1]
    await callback.message.reply(callback.id,
                                 f"Выбрана таймзона {timezone}")
    # Здесь можно добавить логику обработки выбранной таймзоны


# Функция для создания клавиатуры с странами
def get_country_keyboard(letter, page=1):
    countries = [country for country in pycountry.countries if
                 country.name.startswith(letter)]
    countries = countries[(page - 1) * 5:page * 5]
    
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    for country in countries:
        button = InlineKeyboardButton(text=country.name,
                                      callback_data=f'select_country:{country.alpha_2}')
        keyboard_markup.insert(button)
    
    # Добавление кнопок пагинации
    prev_button = InlineKeyboardButton(text='<< Пред.',
                                       callback_data=f'prev_country:{letter}:{page}')
    next_button = InlineKeyboardButton(text='След. >>',
                                       callback_data=f'next_country:{letter}:{page + 1}')
    keyboard_markup.row(prev_button, next_button)
    
    return keyboard_markup


@dp.callback_query_handler(filters.Regexp(r'prev_country:[A-Z]:\d+'))
async def process_prev_country_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split(':')
    letter = data[1]
    page = int(data[2])
    await callback_query.message.edit_text('Страна',
                                           reply_markup=get_country_keyboard(
                                               letter, page - 1))


@dp.callback_query_handler(filters.Regexp(r'next_country:[A-Z]:\d+'))
async def process_next_country_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split(':')
    letter = data[1]
    page = int(data[2])
    await callback_query.message.edit_text('Страна',
                                           reply_markup=get_country_keyboard(
                                               letter, page + 1))


# Функция для создания клавиатуры с таймзонами для выбранной страны
def get_timezone_keyboard(country_code, page=1):
    country = pycountry.countries.get(alpha_2=country_code)
    timezones = pytz.country_timezones.get(country_code, [])
    items_per_page = 5
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    for tz in timezones[start_index:end_index]:
        button = InlineKeyboardButton(text=tz,
                                      callback_data=f'select_timezone:{tz}')
        keyboard_markup.insert(button)
    
    # Добавление кнопок пагинации
    prev_button = InlineKeyboardButton(text='<< Пред.',
                                       callback_data=f'prev_page:{country_code}:{page}')
    next_button = InlineKeyboardButton(text='След. >>',
                                       callback_data=f'next_page:{country_code}:{page + 1}')
    keyboard_markup.row(prev_button, next_button)
    
    return keyboard_markup


@dp.callback_query_handler(filters.Regexp(r'prev_page:[A-Z]{2}:\d+'))
async def process_prev_page_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split(':')
    country_code = data[1]
    page = int(data[2])
    await callback_query.message.edit_text('Таймзона',
                                           reply_markup=get_timezone_keyboard(
                                               country_code, page - 1))


@dp.callback_query_handler(filters.Regexp(r'next_page:[A-Z]{2}:\d+'))
async def process_next_page_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split(':')
    country_code = data[1]
    page = int(data[2])
    await callback_query.message.edit_text('Таймзона',
                                           reply_markup=get_timezone_keyboard(
                                               country_code, page + 1))
