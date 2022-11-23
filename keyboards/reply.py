from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def default_keyboard(buttons: list[str]):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        *list(
            map(
                lambda arg: KeyboardButton(arg),
                sorted(buttons, reverse=True)
            )
        )
    )
    return kb
