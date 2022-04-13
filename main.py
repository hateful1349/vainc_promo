import logging

from aiogram import Bot, Dispatcher
from aiogram import executor as ex
from aiogram import types
from aiogram.types import Message

from creds.token import TOKEN

# from typing import Any


# Initialize Bot instance with an default parse mode which will be passed
# to all API calls
bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

logger = logging.getLogger(__name__)


amdins_id = {
    "389026886",  # bzglve: developer
    "1681304046",  # promo omsk: main admin
}


@dp.message_handler(commands=["start"])
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@dp.message_handler()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward received message back to the sender

    By default message handler will handle all message types
    (like text, photo, sticker and etc.)
    """
    try:
        # Send copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


def main() -> None:
    # And the run events dispatching
    ex.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()


# TODO: возможность отправления карты прому
# TODO: фиксация отчетов
# TODO: получение и выгрузка данных в бд
