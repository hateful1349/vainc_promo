import logging
import os

from aiogram import Bot, Dispatcher
from aiogram import executor as ex
from aiogram.dispatcher.filters.filters import BoundFilter
from aiogram.types import Message

from creds.bot_token import TOKEN
from helpers import get_map_addresses, get_map_picture, get_rand_map

bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

logger = logging.getLogger(__name__)


admins_id = {
    # 389026886,  # bzglve: developer
    1681304046,  # promo omsk: main admin
}

manual_file = os.path.dirname(__file__) + "/src/инструкция.pdf"
flyers_file = os.path.dirname(__file__) + "/src/листовки.jpg"


def parse_addrs(addrs):
    return "\n".join([" ".join(addr[1:3]) for addr in addrs])


class MyFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: Message):
        return message.from_user.id in admins_id


dp.filters_factory.bind(MyFilter)


async def like_wooman(msg: Message):
    await msg.answer("Недостаточно прав для использования данной комманды")


@dp.message_handler(commands=["firstmap"], is_admin=True)
async def firstmap_message_handler(msg: Message):
    """
    Выдать новому прому его первую карту
    """
    # TODO: связь с бд
    # TODO: поиск ближайшего адреса
    # TODO: фотка мапы
    # TODO: отправка инструкции и наших листовок
    await msg.answer_document(open(manual_file, "rb"))
    await msg.answer_photo(open(flyers_file, "rb"), caption="Наши листовки")
    # await msg.answer("Типо выдал новую карту")
    await give_map_handler(msg)


@dp.message_handler(commands=["firstmap"])
async def firstmap_message_handler_prom(msg: Message):
    """
    Первую карту пытается выдать не админ
    """
    await like_wooman(msg)


@dp.message_handler(commands=["map"], is_admin=True)
async def give_map_handler(msg: Message):
    """
    Выдать случайную карту ближе всего к привязанному району
    """
    # TODO: бд
    args = str(msg.get_args())
    if args == "":
        args = get_rand_map()
    for arg in args.split():
        arg = arg.upper()
        map_file = get_map_picture(arg)
        map_addrs = parse_addrs(get_map_addresses(arg))
        if map_file is not None and map_addrs != "":
            with open(map_file, "rb") as map_pic:
                await msg.answer_photo(photo=map_pic, caption=map_addrs)
        else:
            await msg.answer(f'Не найдено адресов или фото карты по запросу "{arg}"')


@dp.message_handler(commands=["map"])
async def give_map_handler_prom(msg: Message):
    """
    Пром пытается сам себе выдать карту
    """
    await like_wooman(msg)


@dp.message_handler(commands=["help"], is_admin=True)
async def help_admin(msg: Message):
    """
    Админ не знает как что работает
    """
    await msg.answer(
        "/map для выдачи случайной карты\n"
        "/map К1-1 для выдачи карты К1-1\n"
        "/map К1-1 К1-2 ... для выдачи сразу нескольких карт\n"
        "/firstmap для выдачи необходимых файлов, регистрации промоутера, выдачи его первой карты в соответствии с его адресом\n"
        "/end для записи в базу информации по пройденной карте"
        "/help для вывода данной справки\n"
    )


@dp.message_handler(commands=["help"])
async def help_prom(msg: Message):
    """
    Пром не знает как пользоваться
    """
    await msg.answer(
        "для вас пока что не предусмотрено какого-то особого функционала, но можете попробовать комманду /end"
    )


@dp.message_handler(commands=["end"])
async def end_map_handler(msg: Message):
    """
    Карта пройдена
    """
    # TODO: бд
    await msg.answer("типо записываю в базу инфу по карте")


def main() -> None:
    ex.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
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
