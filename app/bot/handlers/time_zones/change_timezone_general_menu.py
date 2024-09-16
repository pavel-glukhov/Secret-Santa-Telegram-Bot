import logging

import pycountry
import pytz
from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session
from app.bot.languages import TranslationMainSchema

from app.bot.handlers.operations import get_room_number
from app.bot.handlers.pagination import Pagination
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.time_zones import TimeZoneStates
from app.store.database.queries.users import UserRepo

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith('change_time_zone'))
async def get_letter(callback: types.CallbackQuery,
                     state: FSMContext,
                     app_text_msg: TranslationMainSchema):
    await state.set_state(TimeZoneStates.selecting_letter)
    room_number = get_room_number(callback)

    if room_number:
        await state.update_data(room_number=room_number)

    message_text = app_text_msg.messages.time_zone_menu.letter_of_country

    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=_get_letter_keyboard()
    )

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(TimeZoneStates.selecting_country)


def _get_letter_keyboard():
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    builder = InlineKeyboardBuilder()
    row = []
    for letter in alphabet:
        button = InlineKeyboardButton(text=letter,
                                      callback_data=f'selected_letter:{letter}')
        row.append(button)
        if len(row) == 5:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    return builder.as_markup()


@router.callback_query(F.data.startswith('selected_letter'),
                       StateFilter(TimeZoneStates.selecting_country))
async def process_letter_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        app_text_msg: TranslationMainSchema):
    letter = callback.data.split(':')[-1]
    message_text = app_text_msg.messages.time_zone_menu.select_country
    await callback.message.edit_text(message_text,
                                     reply_markup=get_country_keyboard(
                                         letter))
    await state.set_state(TimeZoneStates.selecting_timezone)


@router.callback_query(F.data.startswith('selected_country'),
                       StateFilter(TimeZoneStates.selecting_timezone))
async def process_country_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        app_text_msg: TranslationMainSchema):
    country_code = callback.data.split(':')[-1]
    message_text = app_text_msg.messages.time_zone_menu.select_timezone
    await callback.message.edit_text(text=message_text,
                                     reply_markup=get_timezone_keyboard(
                                         country_code))
    await state.set_state(TimeZoneStates.confirmation)


@router.callback_query(F.data.startswith('selected_timezone'),
                       StateFilter(TimeZoneStates.confirmation))
async def process_timezone_callback(callback: types.CallbackQuery,
                                    state: FSMContext,
                                    session: Session,
                                    app_text_msg: TranslationMainSchema):
    timezone = callback.data.split(':')[-1]
    state_data = await state.get_data()
    room_number = state_data.get('room_number')

    if room_number:
        callback_query = f"room_start-game_{room_number}"
    else:
        callback_query = "profile_edit"

    message_text = app_text_msg.messages.time_zone_menu.selected_timezone.format(
        timezone=timezone
    )
    keyboard = {
        app_text_msg.buttons.return_back_button: callback_query
    }
    keyboard_inline = generate_inline_keyboard(keyboard)
    await UserRepo(session).update_user(user_id=callback.message.chat.id,
                                        timezone=timezone)
    await callback.message.edit_text(message_text, reply_markup=keyboard_inline)
    await state.clear()


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


@router.callback_query(F.data.regexp(r'prev_country:[A-Z]:\d+'), StateFilter(
    TimeZoneStates.selecting_timezone))
async def process_prev_country_callback(callback: types.CallbackQuery,
                                        app_text_msg: TranslationMainSchema):
    data = callback.data.split(':')
    letter = data[1]
    page = int(data[2])
    message_text = app_text_msg.messages.time_zone_menu.country
    await callback.message.edit_text(message_text,
                                     reply_markup=get_country_keyboard(
                                         letter, page - 1))


@router.callback_query(F.data.regexp(r'next_country:[A-Z]:\d+'),
                       StateFilter(TimeZoneStates.selecting_timezone))
async def process_next_country_callback(callback: types.CallbackQuery,
                                        app_text_msg: TranslationMainSchema):
    data = callback.data.split(':')
    letter = data[1]
    page = int(data[2])
    message_text = app_text_msg.messages.time_zone_menu.country
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


@router.callback_query(F.data.regexp(r'prev_timezone:[A-Z]{2}:\d+'),
                       StateFilter(TimeZoneStates.confirmation))
async def process_prev_timezone_callback(callback_query: types.CallbackQuery,
                                         app_text_msg: TranslationMainSchema):
    data = callback_query.data.split(':')
    country_code = data[1]
    page = int(data[2])
    message_text = app_text_msg.messages.time_zone_menu.timezone
    await callback_query.message.edit_text(message_text,
                                           reply_markup=get_timezone_keyboard(
                                               country_code, page - 1))


@router.callback_query(F.data.regexp(r'next_timezone:[A-Z]{2}:\d+'),
                       StateFilter(TimeZoneStates.confirmation))
async def process_next_timezone_callback(callback_query: types.CallbackQuery,
                                         app_text_msg: TranslationMainSchema):
    data = callback_query.data.split(':')
    country_code = data[1]
    page = int(data[2])
    message_text = app_text_msg.messages.time_zone_menu.timezone
    await callback_query.message.edit_text(message_text,
                                           reply_markup=get_timezone_keyboard(
                                               country_code, page + 1))
