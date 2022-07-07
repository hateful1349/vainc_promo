import difflib
import logging
import os
from typing import List

from aiogram import executor as ex
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from base import bot, dp
from filters import bind_filters
from helpers import (
    collect_addresses,
    collect_maps,
    collect_maps_codes,
    find_matches_map,
    get_map,
    read_config,
)
from polling import add_new_prom
from states import BotStates
from users import Rights

config = read_config()

logging.basicConfig(level=logging.INFO)

sheet_file = os.path.dirname(__file__) + "/src/regions.json"

map_btn = KeyboardButton(text="🗺️ Карта")
addr_btn = KeyboardButton(text="🗺️ Адрес")

choose_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(map_btn, addr_btn)

bind_filters()


@dp.message_handler(commands=["test"], user_have_rights=Rights.CITY)
async def city_handler(msg: Message):
    await msg.answer("У вас есть права CITY")


@dp.message_handler(commands=["test"], user_have_rights=[Rights.CITIES, Rights.GET_MAP])
async def cities_and_getmap_handler(msg: Message):
    await msg.answer("У вас есть права CITIES GET_MAP")


async def woman(msg: Message):
    await msg.answer("Недостаточно прав для использования данной команды")


@dp.message_handler(commands=["firstmap"])
async def firstmap_message_handler_prom(msg: Message):
    """
    Первую карту пытается выдать не админ
    """
    await woman(msg)


@dp.callback_query_handler(lambda c: c.data == "MAP!")
@dp.message_handler(commands=["map"], is_admin=True)
async def give_map_handler(msg: Message | CallbackQuery):
    """
    Отправка карты по встроенной кнопке или команде /map
    """
    if isinstance(msg, CallbackQuery):
        args = msg["message"]["reply_markup"]["inline_keyboard"][0][0]["text"]
        await bot.answer_callback_query(msg.id)
    elif msg.get_args() is not None:
        args = msg.get_args()
    else:
        args = msg["text"]
    for arg in filter(lambda arg: arg in maps_codes, map(str.upper, args.split())):
        map_file, map_addresses = get_map(arg, maps)
        compiled_addresses = "\n".join(
            list(map(lambda address: " ".join(address), map_addresses))
        )
        with open(map_file, "rb") as map_pic:
            if len(compiled_addresses) > 1024:
                await bot.send_photo(msg.from_user.id, map_pic)
                await bot.send_message(msg.from_user.id, compiled_addresses)
            else:
                await bot.send_photo(msg.from_user.id, map_pic, compiled_addresses)


@dp.message_handler(commands=["map"])
async def give_map_handler_prom(msg: Message):
    """
    Пром пытается сам себе выдать карту
    """
    await woman(msg)


@dp.message_handler(state=BotStates.all()[1])
async def give_map_simple(msg: Message):
    """
    Обработка запроса на карту
    """
    await dp.current_state(user=msg.from_user.id).reset_state()
    await give_map_handler(msg)


@dp.message_handler(state=BotStates.all()[2])
async def give_map_by_address_simple(msg: Message):
    """
    Обработка запроса на адрес
    """
    await dp.current_state(user=msg.from_user.id).reset_state()
    await msg.answer(f'Пытаюсь найти по адресу "{msg["text"]}"')
    closest_addresses: List[str] = difflib.get_close_matches(
        msg["text"], addresses, n=5
    )
    if len(closest_addresses) == 0:
        await msg.answer("Кажется я не знаю такого адреса")
        return
    for closest_addr in closest_addresses:
        match_map = find_matches_map(closest_addr, maps)
        answer = f"{closest_addr}: {match_map}"
        await msg.answer(
            answer,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(match_map, callback_data=f"MAP!")
            ),
        )
        if closest_addr.lower() == msg["text"].lower():
            break


@dp.message_handler(Text(equals="🗺️ Карта"), is_admin=True)
async def give_map_message_parser(msg: Message):
    """
    Ловушка для кнопки с картами
    """
    await dp.current_state(user=msg.from_user.id).set_state(BotStates.all()[1])
    await msg.answer("Выберите карту, а я попытаюсь её найти")


@dp.message_handler(Text(equals="🗺️ Адрес"), is_admin=True)
async def handle_address(msg: Message):
    """
    Ловушка для кнопки с адресами
    """
    await dp.current_state(user=msg.from_user.id).set_state(BotStates.all()[2])
    await msg.answer("Какой адрес ищем?")


@dp.message_handler(commands=["start"], is_admin=True)
async def start_handler(msg: Message):
    """
    Стартовое сообщение, показывающее кнопки
    """
    await msg.reply("Приветствую", reply_markup=choose_kb)


@dp.message_handler(commands=["help"], is_admin=True)
async def help_admin(msg: Message):
    """
    Админ не знает как что работает
    """
    await msg.answer(
        "/map для выдачи случайной карты\n"
        "/map К1-1 для выдачи карты К1-1\n"
        "/map К1-1 К1-2 ... для выдачи сразу нескольких карт\n"
        "/firstmap для выдачи необходимых файлов, "
        "регистрации промоутера, выдачи его "
        "первой карты в соответствии с его адресом\n"
        "/end для записи в базу информации по пройденной карте\n"
        "/help для вывода данной справки\n"
    )


@dp.message_handler(commands=["help"])
async def help_prom(msg: Message):
    """
    Пром не знает как пользоваться
    """
    await msg.answer(
        "для вас пока что не предусмотрено какого-то особого "
        "функционала, но можете попробовать команду /end"
    )


@dp.message_handler()
async def handle_text(msg: Message):
    """
    Обработка всех возможных сообщений
    """
    await msg.answer("Возможно вы сейчас пытаетесь получить какой-то адрес или карту")
    await msg.answer(
        "Теперь это работает только по кнопкам ниже", reply_markup=choose_kb
    )


def main() -> None:
    # ex.start_polling(dp, skip_updates=True)
    ex.start_polling(dp)


if __name__ == "__main__":
    maps = collect_maps(sheet_file)
    addresses = collect_addresses(maps)
    maps_codes = collect_maps_codes(maps)
    main()

# TODO: возможность отправления карты прому
# TODO: фиксация отчетов
# TODO: получение и выгрузка данных в бд

# firstmap
# реализация:
#   отправляет промоутеру инструкцию, наши листовку
#   а также первую карту с его домом или максимально близкую к нему
#   добавляет эту карту в буфер тестовых
#   фиксирует прома его карту и выдачу 300 листовок в базу
# права:
#   админ

# end
#   завершение карты по факту
#   фиксирует дату завершения карты
#   считает количество разложенного материала для расчета зарплаты
#   сравнивает время выдачи карты с текущим для бонуса за проезд

# givemap
# выдает самую близкую к дому свободную карту
#
# только для админа

# givemap О1-4
# выдаст карту О1-4
