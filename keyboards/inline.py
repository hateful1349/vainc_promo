from aiogram import types


def simple_kb(data: dict, row_width=None):
    if row_width:
        return types.InlineKeyboardMarkup(row_width=row_width).add(
            *list(
                map(
                    lambda btn_text, btn_callback: types.KeyboardButton(btn_text, callback_data=btn_callback),
                    data.keys(), data.values()
                )
            )
        )
    else:
        return types.InlineKeyboardMarkup().add(
            *list(
                map(
                    lambda btn_text, btn_callback: types.KeyboardButton(btn_text, callback_data=btn_callback),
                    data.keys(), data.values()
                )
            )
        )
