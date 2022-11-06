from aiogram import types
from aiogram.dispatcher.filters import Text

from loader import dp


@dp.message_handler(Text(equals="Отмена"), state="*")
@dp.message_handler(commands=["cancel"], state="*")
async def cancel_handler(msg: types.Message):
    await dp.current_state(user=msg.from_user.id).reset_state()
    from handlers.default.handlers import handle_text

    await handle_text(msg)
