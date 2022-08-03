from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_map_menu(city, map_name):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(map_name, callback_data=f"MAP&CITY={city}&MAPS={map_name}")
    )
    return kb
