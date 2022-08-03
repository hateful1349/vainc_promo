from aiogram import types
from keyboards.default.keyboards import get_start_keyboard
from loader import dp
from utils.users import Users


@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    """
    Стартовое сообщение, показывающее кнопки
    """
    await handle_text(msg)


@dp.message_handler(commands=["help"])
async def help_admin(msg: types.Message):
    """
    Админ не знает как что работает
    """
    await handle_text(msg)


@dp.message_handler()
async def handle_text(msg: types.Message):
    """
    Обработка всех возможных сообщений
    """
    lines = Users.get_user_actions(msg.from_user.id)
    if len(lines) == 0:
        await msg.answer(
            f"Вы не можете использовать данного бота\nЕсли вы считаете, что это ошибка, то обратитесь к вышестоящему лицу за подробностями",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await msg.answer(
            "Все возможные для вас действия можно сделать по кнопкам ниже",
            reply_markup=get_start_keyboard(lines),
        )