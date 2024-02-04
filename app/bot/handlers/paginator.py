import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def paginator(objects: list,
              page_size: int,
              page: int,
              obj_callback_prefix: str,
              callback_next_prefix: str,
              callback_back_prefix: str,
              keyboard_query: dict['str': bool, 'str':str],
              obj_keyboard_method: str | None = None):
    """
    keyboard_query = {'object': True|False,
                      'method_or_name': 'class_method or name'}
    """
    items_per_page = page_size
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    total_pages = math.ceil(len(objects) / items_per_page)
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    
    for obj in objects[start_index:end_index]:
        
        if not keyboard_query.get('object'):
            keyboard_text = keyboard_query.get('method_or_name')
        
        if (keyboard_query.get('object')
                and keyboard_query.get('method_or_name')):
            keyboard_text = getattr(obj, keyboard_query.get('method_or_name'))
        
        if (keyboard_query.get('object')
                and not keyboard_query.get('method_or_name')):
            keyboard_text = obj
        
        if obj_keyboard_method:
            callback_query = getattr(obj, obj_keyboard_method)
        else:
            callback_query = obj
        
        button = InlineKeyboardButton(
            text=keyboard_text,
            callback_data=(
                f'{obj_callback_prefix}:{callback_query}'
            )
        )
        keyboard_markup.insert(button)
    
    keyboard_count_pages = InlineKeyboardButton(
        text=f'({page}/{total_pages})',
        callback_data='non_click_count_pages'
    )
    empty_button = InlineKeyboardButton(
        text='  ',
        callback_data='non_click_button_disabled'
    
    )
    prev_button = InlineKeyboardButton(
        text='◀️',
        callback_data=f'{callback_back_prefix}:{page}'
    )
    next_button = InlineKeyboardButton(
        text='➡️',
        callback_data=f'{callback_next_prefix}:{page}'
    )
    if len(objects) > items_per_page:
        if page == 1 and page < end_index < len(objects):
            keyboard_markup.row(empty_button, keyboard_count_pages,
                                next_button)
        
        if 1 < page < end_index < len(objects):
            keyboard_markup.row(prev_button, keyboard_count_pages,
                                next_button)
        
        if page > 1 and page == total_pages:
            keyboard_markup.row(prev_button, keyboard_count_pages,
                                empty_button)
    
    return keyboard_markup
