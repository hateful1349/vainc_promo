import difflib
import logging
from typing import Union

from aiogram import executor as ex
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Document
)

from base import bot, dp
from tools.database import Database as db
from filters import bind_filters
from helpers import parse_callback_data

from states import BotStates
from users import Rights, Users

logging.basicConfig(level=logging.INFO)

bind_filters()


async def woman(msg: Message):
    await msg.answer(
        "Недостаточно прав для использования данной команды",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.callback_query_handler(lambda c: parse_callback_data(c.data).get("url") == "MAP")
@dp.message_handler(state=BotStates.MAP)
@dp.message_handler(commands=["map"], user_have_rights=Rights.GET_MAP)
async def give_user_map(msg: Union[Message, CallbackQuery], state: FSMContext = None):
    """
    Отправка карты по встроенной кнопке, команде /map или на текстовый запрос карты
    """
    city = None
    required_maps = None
    if state:
        async with state.proxy() as data:
            city = data.get("city")
    if isinstance(msg, CallbackQuery):
        await bot.answer_callback_query(msg.id)
        # city = list(filter(lambda c: "CITY" in c, callback_args))[0].split("=")[1]
        city = parse_callback_data(msg.data).get("CITY")
        # required_maps = (list(filter(lambda c: "MAPS" in c, callback_args))[0].split("=")[1].split())
        required_maps = parse_callback_data(msg.data).get("MAPS").split()
    else:
        args = (
            msg.get_args()
        )  # возвращает пустую строку если команда /map без аргументов и None если сообщение пришло из другого места программы в тупо тестовом формате, без /map в формате "К1-1 К2-2"
        if args == "":
            await msg.answer("Нельзя просто так вызывать пустую команду")
        elif args is None:
            required_maps = msg["text"].split()
        else:
            args = args.split()
            user_cities = Users.get_user_cities(msg.from_user.id)
            if len(user_cities) > 1:
                if args[0] not in list(
                    map(lambda city: city.name.lower(), db.get_cities())
                ):
                    await msg.answer(
                        "Какой вам нужен город?",
                        reply_markup=InlineKeyboardMarkup().add(
                            *list(
                                map(
                                    lambda city: InlineKeyboardButton(
                                        city,
                                        # callback_data=f"CITY={city}&MAPS={' '.join(args)}",
                                        callback_data=f"MAP&CITY={city}&MAPS={' '.join(args)}",
                                    ),
                                    user_cities,
                                )
                            )
                        ),
                    )
                else:
                    city = args[0]
                    required_maps = args[1:]
            else:
                city = user_cities[0]
                required_maps = args

    if city and required_maps:
        if city.lower() not in list(
            map(lambda city: city.name.lower(), db.get_cities())
        ):
            await bot.send_message(
                msg.from_user.id, f'У меня пока нет данных по городу "{city}"'
            )
            await dp.current_state(user=msg.from_user.id).reset_state()
            return
        for required_map in map(str.upper, required_maps):
            mp = db.get_map(required_map, city)
            if not mp:
                await bot.send_message(
                    msg.from_user.id, f"Я не знаю карты {required_map}"
                )
                continue
            compiled_addresses = "\n".join(
                [f"Карта: {mp.name}"]
                + list(
                    map(
                        lambda address: " ".join([address.street, address.number]),
                        mp.addresses,
                    )
                )
            )
            # with open(map_file, "rb") as map_pic:
            if len(compiled_addresses) > 1024:
                await bot.send_photo(msg.from_user.id, mp.picture)
                await bot.send_message(msg.from_user.id, compiled_addresses)
            else:
                await bot.send_photo(msg.from_user.id, mp.picture, compiled_addresses)

    await dp.current_state(user=msg.from_user.id).reset_state()


@dp.message_handler(state=BotStates.ADDRESS)
async def give_map_by_address(msg: Message, state: FSMContext = None):
    """
    Обработка запроса на адрес
    """
    city = None
    if state:
        async with state.proxy() as data:
            city = data.get("city")
    closest_addresses = difflib.get_close_matches(
        msg.text.lower(),
        map(
            str.lower,
            list(
                map(
                    lambda address: f"{address.street} {address.number}",
                    db.get_addresses(city),
                )
            ),
        ),
        n=5,
    )
    if len(closest_addresses) == 0:
        await msg.answer("Кажется я не знаю такого адреса")
        await dp.current_state(user=msg.from_user.id).reset_state()
        return
    if msg.text.lower() in closest_addresses:
        closest_addresses = [msg.text.lower()]
    for closest_address in closest_addresses:
        match_map = db.get_matches_map(
            (closest_address.rsplit(" ")[0], closest_address.rsplit(" ")[1]), city
        ).name
        await msg.answer(
            closest_address,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    match_map, callback_data=f"MAP&CITY={city}&MAPS={match_map}"
                )
            ),
        )

    await dp.current_state(user=msg.from_user.id).reset_state()


@dp.callback_query_handler(lambda c: "QUERY_CITY_MAP" in c.data)
@dp.message_handler(
    Text(equals=Rights.comments.get(Rights.GET_MAP)), user_have_rights=Rights.GET_MAP
)
async def give_map_message_parser(
    msg: Message | CallbackQuery, state: FSMContext = None
):
    """
    Ловушка для кнопки с картами
    """
    city = None
    if isinstance(msg, Message):
        user_cities = Users.get_user_cities(msg.from_user.id)
        if user_cities is None:
            await msg.answer(
                "⚠️ У вас не задан город. Обратитесь к вышестоящему лицу за подробностями"
            )
        elif len(user_cities) > 1:
            await msg.answer(
                "Какой вам нужен город?",
                reply_markup=InlineKeyboardMarkup().add(
                    *list(
                        map(
                            lambda city: InlineKeyboardButton(
                                city,
                                callback_data=f"QUERY_CITY_MAP={city}",
                            ),
                            user_cities,
                        )
                    )
                ),
            )
        else:
            city = user_cities[0]
    elif isinstance(msg, CallbackQuery):
        await bot.answer_callback_query(msg.id)
        city = msg.data.split("=")[-1]
    if city:
        async with state.proxy() as data:
            data["city"] = city
        await BotStates.MAP.set()
        await bot.send_message(msg.from_user.id, "Какую карту ищем?")


@dp.callback_query_handler(lambda c: "QUERY_CITY_ADDRESS" in c.data)
@dp.message_handler(
    Text(equals=Rights.comments.get(Rights.GET_ADDRESS)),
    user_have_rights=Rights.GET_ADDRESS,
)
async def handle_address(msg: Message | CallbackQuery, state: FSMContext = None):
    """
    Ловушка для кнопки с адресами
    """
    city = None
    if isinstance(msg, Message):
        user_cities = Users.get_user_cities(msg.from_user.id)
        if user_cities is None:
            await msg.answer(
                "⚠️ У вас не задан город. Обратитесь к вышестоящему лицу за подробностями"
            )
        elif len(user_cities) > 1:
            await msg.answer(
                "Какой вам нужен город?",
                reply_markup=InlineKeyboardMarkup().add(
                    *list(
                        map(
                            lambda city: InlineKeyboardButton(
                                city,
                                callback_data=f"QUERY_CITY_ADDRESS={city}",
                            ),
                            user_cities,
                        )
                    )
                ),
            )
        else:
            city = user_cities[0]
    elif isinstance(msg, CallbackQuery):
        await bot.answer_callback_query(msg.id)
        city = msg.data.split("=")[-1]
    if city:
        async with state.proxy() as data:
            data["city"] = city
        await BotStates.ADDRESS.set()
        await bot.send_message(msg.from_user.id, "Какой адрес интересует?")


@dp.callback_query_handler(lambda c: parse_callback_data(c.data).get("url") == "RIGHTS")
@dp.message_handler(
    Text(equals=Rights.comments.get(Rights.CHANGE_USER_PERMISSIONS)),
    user_have_rights=[Rights.CHANGE_USER_PERMISSIONS],
)
async def test(msg: Message | CallbackQuery):
    menu = (
        "START"
        if isinstance(msg, Message)
        else parse_callback_data(msg.data).get("MENU") or "START"
    )
    print("CURRENT_MENU:", menu)
    chosen_user = None
    if isinstance(msg, CallbackQuery):
        fields = parse_callback_data(msg.data)
        if menu == "USER_MENU":
            chosen_user = fields.get("USER")
    users = Users.get_users()
    user_managers = Users.get_management(msg.from_user.id)
    menus = {
        "START": {
            "text": "Кого покараем/наградим?",
            "buttons": list(
                map(
                    lambda user: InlineKeyboardButton(
                        users[user]["username"] or users[user]["name"] or user,
                        callback_data=f"RIGHTS&MENU=USER_MENU&USER={user}",
                    ),
                    filter(
                        lambda user: user
                        not in user_managers
                        | {
                            str(msg.from_user.id),
                        },
                        list(users.keys()),
                    ),
                )
            ),
        },
        "USER_MENU": {
            "text": Users.get_information(chosen_user) if chosen_user else "",
            "buttons": [
                KeyboardButton(
                    "🏙️ Город",
                    callback_data=f"RIGHTS&MENU=CHANGE_CITY&USER={chosen_user}",
                ),
                KeyboardButton(
                    "🔑 Права",
                    callback_data=f"RIGHTS&MENU=CHANGE_RIGHTS&USER={chosen_user}",
                ),
                KeyboardButton(
                    "💾 Данные",
                    callback_data=f"RIGHTS&MENU=CHANGE_DATA&USER={chosen_user}",
                ),
                KeyboardButton(
                    "💾 Начальство",
                    callback_data=f"RIGHTS&MENU=CHANGE_MANAGERS&USER={chosen_user}",
                ),
                KeyboardButton("🔙 Назад", callback_data="RIGHTS"),
            ],
        },
    }

    if isinstance(msg, Message):
        await msg.answer(
            menus.get(menu).get("text"),
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                *menus.get(menu).get("buttons")
            ),
        )
    else:
        await bot.answer_callback_query(msg.id)
        await bot.edit_message_text(
            chat_id=msg.message.chat.id,
            message_id=msg.message.message_id,
            text=menus.get(menu).get("text"),
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                *menus.get(menu).get("buttons")
            ),
        )


@dp.message_handler(state=BotStates.WAIT_FOR_CITY_RESOURCES, content_types=["document"])
async def get_city_resources(msg: Document, state: FSMContext = None):
    file_id = msg.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await msg.answer(f"file_path: {file_path}")
    async with state.proxy() as data:
        if files := data.get("files"):
            if len(files) < 2:
                files.append(file_path)
            if len(files) == 2:
                await msg.answer(f"files: {files}")
                await dp.current_state(user=msg.from_user.id).reset_state()
        else:
            data["files"] = [file_path]
    async with state.proxy() as data:
        print(data.get("files"))


@dp.message_handler(Text(equals=Rights.comments.get(Rights.CITY_MANAGEMENT)),
    user_have_rights=[Rights.CITY_MANAGEMENT])
async def change_city(msg: Message):
    await msg.answer("Тут ща будет добавление нового города")
    await msg.answer("Отправь мне в одном сообщении zip архив с картами и xlsx таблицу с адресами")
    await BotStates.WAIT_FOR_CITY_RESOURCES.set()

@dp.message_handler(commands=["start"])
async def start_handler(msg: Message):
    """
    Стартовое сообщение, показывающее кнопки
    """
    await handle_text(msg)


@dp.message_handler(commands=["help"])
async def help_admin(msg: Message):
    """
    Админ не знает как что работает
    """
    await handle_text(msg)


@dp.message_handler()
async def handle_text(msg: Message):
    """
    Обработка всех возможных сообщений
    """
    lines = Users.get_user_actions(msg.from_user.id)
    if len(lines) == 0:
        await msg.answer(
            f"Вы не можете использовать данного бота\nЕсли вы считаете, что это ошибка, то обратитесь к главным администраторам {' '.join(Users.get_main_admins())}",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        choose_kb = ReplyKeyboardMarkup(resize_keyboard=True)
        choose_kb.add(*list(map(lambda l: KeyboardButton(l), lines)))
        await msg.answer(
            "Все возможные для вас действия можно сделать по кнопкам ниже",
            reply_markup=choose_kb,
        )


def main() -> None:
    # ex.start_polling(dp, skip_updates=True)
    ex.start_polling(dp)


if __name__ == "__main__":
    main()


# TODO: допилить изменение прав пользователей
# TODO: разные меню
# TODO: подменю
# TODO: пролистываение пунктов меню
# TODO: запрет на изменение прав конкретных пользователей, либо вышестоящего руководства
# TODO: запрет на изменение своих прав
