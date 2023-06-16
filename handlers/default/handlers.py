from aiogram import types

from database.users import Users
from keyboards.reply import default_keyboard
from loader import dp
from utils.messages.messages import Messages


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
            Messages.default_message_null,
            reply_markup=types.ReplyKeyboardRemove(),  # type: ignore
        )
    else:
        await msg.answer(
            Messages.default_message_rights,
            reply_markup=default_keyboard(lines),
        )
