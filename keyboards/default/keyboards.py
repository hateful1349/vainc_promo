from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_start_keyboard(args: list):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*list(map(lambda arg: KeyboardButton(arg), sorted(args, reverse=True))))
    return kb
