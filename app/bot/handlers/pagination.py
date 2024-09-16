import math
from typing import Any

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Pagination:
    def __init__(
            self, objects: Any,
            page_size: int,
            callback_next_prefix: str,
            callback_back_prefix: str,
            callback_prefix: str | None = None,
            keyboard_name_or_method: str | None = None,
            callback_name_or_method: str | None = None
    ):
        self.objects = objects
        self.page_size = page_size
        self.callback_next_prefix = callback_next_prefix
        self.callback_back_prefix = callback_back_prefix
        self.callback_prefix = callback_prefix
        self.object_attribute_for_keyboard_name = keyboard_name_or_method
        self.object_attribute_for_callback = callback_name_or_method

    def inline_pagination(self, page: int):
        data = self._data_splitter(page, self.objects)
        collection = data.get('collection')
        total_pages = data.get('total_pages')
        end_index = data.get('end_index')
        builder = InlineKeyboardBuilder()
        for item in collection:
            if self.object_attribute_for_keyboard_name:
                keyboard_text = getattr(item,
                                        self.object_attribute_for_keyboard_name)
            else:
                keyboard_text = item

            if self.object_attribute_for_callback:
                callback_query = getattr(item,
                                         self.object_attribute_for_callback)
            else:
                callback_query = item

            button = InlineKeyboardButton(
                text=keyboard_text,
                callback_data=(
                    f'{self.callback_prefix}:{callback_query}'
                )
            )
            builder.row(button)

        pagination_keyboard = self._pagination_keyboard_generator(
            builder,
            page,
            total_pages,
            end_index)

        return pagination_keyboard

    def _data_splitter(self, page: int, objects: list[Any]) -> dict:
        start_index = (page - 1) * self.page_size
        end_index = start_index + self.page_size
        total_pages = math.ceil(len(objects) / self.page_size)
        return {
            'collection': objects[start_index:end_index],
            'total_pages': total_pages,
            'start_index': start_index,
            'end_index': end_index
        }

    def _pagination_keyboard_generator(self,
                                       keyboard_builder,
                                       page,
                                       total_pages,
                                       end_index):
        count_button = InlineKeyboardButton(
            text=f'({page}/{total_pages})', callback_data='non_click_count_pages'
        )
        empty_button = InlineKeyboardButton(
            text='  ', callback_data='non_click_button_disabled'
        )
        prev_button = InlineKeyboardButton(
            text='◀️', callback_data=f'{self.callback_back_prefix}:{page}'
        )
        next_button = InlineKeyboardButton(
            text='➡️', callback_data=f'{self.callback_next_prefix}:{page}'
        )
        if len(self.objects) > self.page_size:
            if page == 1 and page < end_index < len(self.objects):
                keyboard_builder.row(empty_button, count_button, next_button)

            if 1 < page < end_index < len(self.objects):
                keyboard_builder.row(prev_button, count_button, next_button)

            if page > 1 and page == total_pages:
                keyboard_builder.row(prev_button, count_button, empty_button)

        return keyboard_builder.as_markup()
