from aiogram import executor as ex

import filters
import handlers
from loader import dp
from utils.commands import set_default_commands


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)


async def shutdown(dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == "__main__":
    # ex.start_polling(dp, skip_updates=True)
    ex.start_polling(dp, on_startup=on_startup, on_shutdown=shutdown)


# TODO: допилить изменение прав пользователей
# TODO: разные меню
# TODO: подменю
# TODO: пролистываение пунктов меню
# TODO: запрет на изменение прав конкретных пользователей, либо вышестоящего руководства
# TODO: запрет на изменение своих прав
