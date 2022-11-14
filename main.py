import logging

from aiogram import executor as ex

import filters
import handlers
from loader import dp
from utils.commands import set_default_commands


async def on_startup(dispatcher):
    logging.info("startup setup")
    await set_default_commands(dispatcher)


async def shutdown(dispatcher):
    logging.error("shutting down")
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == "__main__":
    logging.info("bot starting")
    ex.start_polling(
        dp, on_startup=on_startup, on_shutdown=shutdown, skip_updates=False
    )
