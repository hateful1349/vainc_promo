from aiogram.types import BotCommand


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            BotCommand("start", "Запустить бота"),
            BotCommand("help", "Вывести справку"),
            BotCommand("map", "Выдать карту"),
            # BotCommand("test", "Тестируемая фича"),
        ]
    )
