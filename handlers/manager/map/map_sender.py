from aiogram.utils import exceptions, markdown

from database.database import Database
from loader import bot


async def send_map(chat_id, city=None, map_id=None, map_name=None, map_obj=None):
    if map_obj:
        mp = map_obj
    elif map_id:
        mp = Database.get_map(city, map_id=map_id)
    elif map_name:
        mp = Database.get_map(city, map_name=map_name)
    else:
        print("Надо хоть что-то задать типо айдишника или имени карты, а ты даун - нихуя")
        return
    if mp is None:
        print(city, map_id, map_name, map_obj)
        await bot.send_message(chat_id, "Я не знаю такой карты")
        return

    text = "\n".join(([markdown.hbold(f"Карта: {mp.name}")] + list(
        map(lambda address: " ".join([address.street or '', address.number or '']),
            Database.get_addresses(map_id=mp.id)))))

    try:
        await bot.send_photo(chat_id, mp.picture, text)
    except exceptions.BadRequest:
        await bot.send_photo(chat_id, mp.picture)
        await bot.send_message(chat_id, text)
