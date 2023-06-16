import logging

from aiogram.types import BotCommand


async def set_default_commands(dp):
    logging.info("default commands setup")
    await dp.bot.set_my_commands(
        [
            BotCommand(
                "start",
                "Запустить бота",
            ),
            BotCommand("help", "Вывести справку"),
            # BotCommand("map", "Выдать карту"),
            # BotCommand("address", "Найти карту по адресу"),
            BotCommand("cancel", "Отмена"),
            # BotCommand("test", "Тестируемая фича"),
        ]
    )
