import difflib
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram import executor as ex
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.filters import BoundFilter
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.helper import Helper, HelperMode, ListItem

from helpers import (
    collect_addrs,
    collect_maps,
    collect_maps_codes,
    find_matches_map,
    get_map,
    read_config,
)

config = read_config()
bot = Bot(config["TG"]["bot_token"], parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

logging.basicConfig(level=logging.DEBUG)

admins_id = set(config["TG"]["admins"].split())

flyers_file = os.path.dirname(__file__) + "/src/листовки.jpg"
sheet_file = os.path.dirname(__file__) + "/src/regions.json"
addrs = list()
maps_codes = list()
maps = dict()


map_btn = KeyboardButton(text="🗺️ Карта")
addr_btn = KeyboardButton(text="🗺️ Адрес")

choose_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(map_btn, addr_btn)


class AdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin: str):
        self.is_admin = is_admin

    async def check(self, message: Message):
        return str(message.from_user.id) in admins_id


dp.filters_factory.bind(AdminFilter)


#### states ####
class BotStates(Helper):
    mode = HelperMode.snake_case

    DEFAULT = ListItem()
    MAP = ListItem()
    ADDRESS = ListItem()


async def wooman(msg: Message):
    await msg.answer("Недостаточно прав для использования данной комманды")


@dp.message_handler(commands=["firstmap"], is_admin=True)
async def firstmap_message_handler(msg: Message):
    """
    Выдать новому прому его первую карту
    """
    # TODO: связь с бд
    # TODO: поиск ближайшего адреса
    await msg.answer_photo(open(flyers_file, "rb"), caption="Наши листовки")
    await give_map_handler(msg)


@dp.message_handler(commands=["firstmap"])
async def firstmap_message_handler_prom(msg: Message):
    """
    Первую карту пытается выдать не админ
    """
    await wooman(msg)


@dp.callback_query_handler(lambda c: c.data == "MAP!")
@dp.message_handler(commands=["map"], is_admin=True)
async def give_map_handler(msg: Message | CallbackQuery):
    """
    Отправка карты по инлайн кнопке или команде /map
    """
    if isinstance(msg, CallbackQuery):
        args = msg["message"]["reply_markup"]["inline_keyboard"][0][0]["text"]
        await bot.answer_callback_query(msg.id)
    elif msg.get_args() is not None:
        args = msg.get_args()
    else:
        args = msg["text"]
    for arg in [a.upper() for a in args.split() if a.upper() in maps_codes]:
        map_file, map_addrs = get_map(arg, maps)
        compiled_addrs = "\n".join([" ".join(addr) for addr in map_addrs])
        with open(map_file, "rb") as map_pic:
            if len(compiled_addrs) > 1032:
                await bot.send_photo(msg.from_user.id, map_pic)
                await bot.send_message(msg.from_user.id, compiled_addrs)
            else:
                await bot.send_photo(msg.from_user.id, map_pic, compiled_addrs)


@dp.message_handler(commands=["map"])
async def give_map_handler_prom(msg: Message):
    """
    Пром пытается сам себе выдать карту
    """
    await wooman(msg)


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
    Обработака запроса на адрес
    """
    await dp.current_state(user=msg.from_user.id).reset_state()
    await msg.answer(f'Пытаюсь найти по адресу "{msg["text"]}"')
    closest_addrs = difflib.get_close_matches(msg["text"], addrs, n=5)
    if len(closest_addrs) == 0:
        await msg.answer("Кажется я не знаю такого адреса")
        return
    for closest_addr in closest_addrs:
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
        "функционала, но можете попробовать комманду /end"
    )


@dp.message_handler(commands=["end"])
async def end_map_handler(msg: Message):
    """
    Карта пройдена
    """
    # TODO: бд
    await msg.answer("типо записываю в базу инфу по карте")


# text handler
# @dp.message_handler(is_admin=True)
@dp.message_handler()
async def handle_text(msg: Message):
    """
    Обработка всех возможных сообщений
    """
    await msg.answer("возможно вы сейчас пытаетесь получить какой-то адрес или карту")
    await msg.answer("теперь это работает только по кнопкам ниже", reply_markup=choose_kb)


def main() -> None:
    # ex.start_polling(dp, skip_updates=True)
    ex.start_polling(dp)


if __name__ == "__main__":
    maps = collect_maps(sheet_file)
    addrs = collect_addrs(maps)
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
#   считает количество разложенного материала для рассчета зарплаты
#   сравнивает время выдачи карты с текущим для бонуса за проезд

# givemap
# выдает самую близкую к дому свободную карту
#
# только для админа

# givemap О1-4
# выдаст карту О1-4
