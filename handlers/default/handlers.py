from aiogram import types

from database.users import Users
from keyboards.default.keyboards import get_start_keyboard
from loader import dp


@dp.message_handler(commands=["start"], state="*")
async def start_handler(msg: types.Message):
    await handle_text(msg)


@dp.message_handler(commands=["help"], state="*")
async def help_admin(msg: types.Message):
    await handle_text(msg)


@dp.message_handler(state="*")
async def handle_text(msg: types.Message):
    lines = Users.get_user_actions(msg.from_user.id)
    if len(lines) == 0:
        await msg.answer(
            f"Вы не можете использовать данного бота\n"
            f"Если вы считаете, что это ошибка, то обратитесь к вышестоящему лицу за подробностями",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await msg.answer(
            "Все возможные для вас действия можно сделать по кнопкам ниже",
            reply_markup=get_start_keyboard(lines),
        )
