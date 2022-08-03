import difflib
from typing import Union

import sqlalchemy
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from database.database import Database as db
from keyboards.inline.keyboards import get_map_menu
from loader import bot, dp
from states.states import BotStates
from utils.callback import parse_callback_data
from utils.users import Rights, Users
from aiogram.utils import markdown


@dp.callback_query_handler(lambda c: parse_callback_data(c.data).get("url") == "MAP")
@dp.message_handler(state=BotStates.MAP)
@dp.message_handler(commands=["map"], user_have_rights=Rights.GET_MAP)
async def give_user_map(
    msg: Union[types.Message, types.CallbackQuery], state: FSMContext = None
):
    """
    Отправка карты по встроенной кнопке, команде /map или на текстовый запрос карты
    """
    city = None
    required_maps = None
    if state:
        async with state.proxy() as data:
            city = data.get("city")
    if isinstance(msg, types.CallbackQuery):
        await bot.answer_callback_query(msg.id)
        city = parse_callback_data(msg.data).get("CITY")
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
                ):  # ! не работает, вероятно нахуй надо
                    kb = types.InlineKeyboardMarkup().add(
                        *list(
                            map(
                                lambda city: types.InlineKeyboardButton(
                                    city,
                                    callback_data=f"MAP&CITY={city}&MAPS={' '.join(args)}",
                                ),
                                user_cities,
                            )
                        )
                    )
                    await msg.answer("Какой вам нужен город?", reply_markup=kb)
                else:
                    city = args[0]
                    required_maps = args[1:]
            # return (
            #     session.query(Map)
            #     .join(Region, Region.region_id == Map.region_id)
            #     .join(City, City.region_id == Region.region_id)
            #     .join(Address, Address.map_id == Map.map_id)
            #     .filter(City.name.like(city))
            #     .filter(Address.street.like(address[0]))
            #     .filter(Address.number.like(address[1])).first()
            # )
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
            mp = None
            try:
                mp = db.get_map(required_map, city)
            except sqlalchemy.exc.OperationalError as e:
                await bot.send_message(
                    msg.from_user.id,
                    f"Я от вас жду сносное название карты, а не {required_map}",
                )

            if not mp:
                await bot.send_message(
                    msg.from_user.id, f"Я не знаю карты {required_map}"
                )
                continue
            compiled_addresses = "\n".join(
                [markdown.bold(f"Карта: {mp.name}")]
                + list(
                    map(
                        lambda address: " ".join([address.street, address.number]),
                        mp.addresses,
                    )
                )
            )
            if len(compiled_addresses) > 1024: # если размер описания к фото слишком большой, то отправить два отдельных сообщения
                await bot.send_photo(msg.from_user.id, mp.picture)
                await bot.send_message(msg.from_user.id, compiled_addresses)
            else:
                await bot.send_photo(msg.from_user.id, mp.picture, compiled_addresses)

    await dp.current_state(user=msg.from_user.id).reset_state()


@dp.message_handler(state=BotStates.ADDRESS)
async def give_map_by_address(msg: types.Message, state: FSMContext = None):
    """
    Обработка запроса на адрес
    """
    city = None
    if state:
        async with state.proxy() as data:
            city = data.get("city")
    addresses = db.get_addresses(city)
    closest_addresses_str = difflib.get_close_matches(
        msg.text.lower(),
        map(
            str.lower,
            list(map(lambda address: f"{address.street} {address.number}", addresses)),
        ),
        n=5,
    )

    if not closest_addresses_str:
        await msg.answer("Кажется я не знаю такого адреса")
        await dp.current_state(user=msg.from_user.id).reset_state()
        return
    if msg.text.lower() in closest_addresses_str:
        closest_addresses_str = [msg.text.lower()]
    closest_addresses = list(
        filter(
            lambda address: f"{address.street} {address.number}".lower()
            in closest_addresses_str,
            addresses,
        )
    )
    for closest_address in closest_addresses:
        await msg.answer(
            f"{closest_address.street} {closest_address.number}",
            reply_markup=get_map_menu(city, closest_address.map2.name),
        )
    await dp.current_state(user=msg.from_user.id).reset_state()


@dp.callback_query_handler(lambda c: "QUERY_CITY_MAP" in c.data)
@dp.message_handler(
    Text(equals=Rights.comments.get(Rights.GET_MAP)),
    user_have_rights=Rights.GET_MAP,
)
async def give_map_message_parser(
    msg: Union[types.Message, types.CallbackQuery], state: FSMContext = None
):
    """
    Ловушка для кнопки с картами
    """
    city = None
    if isinstance(msg, types.Message):
        user_cities = Users.get_user_cities(msg.from_user.id)
        if user_cities is None:
            await msg.answer(
                "⚠️ У вас не задан город. Обратитесь к вышестоящему лицу за подробностями"
            )
        elif len(user_cities) > 1:
            kb = types.InlineKeyboardMarkup().add(
                *list(
                    map(
                        lambda city: types.InlineKeyboardButton(
                            city,
                            callback_data=f"QUERY_CITY_MAP={city}",
                        ),
                        user_cities,
                    )
                )
            )
            await msg.answer("Какой вам нужен город?", reply_markup=kb)
        else:
            city = user_cities[0]
    elif isinstance(msg, types.CallbackQuery):
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
async def handle_address(
    msg: Union[types.Message, types.CallbackQuery], state: FSMContext = None
):
    """
    Ловушка для кнопки с адресами
    """
    city = None
    if isinstance(msg, types.Message):
        user_cities = Users.get_user_cities(msg.from_user.id)
        if user_cities is None:
            await msg.answer(
                "⚠️ У вас не задан город. Обратитесь к вышестоящему лицу за подробностями"
            )
        elif len(user_cities) > 1:
            kb = types.InlineKeyboardMarkup().add(
                *list(
                    map(
                        lambda city: types.InlineKeyboardButton(
                            city,
                            callback_data=f"QUERY_CITY_ADDRESS={city}",
                        ),
                        user_cities,
                    )
                )
            )
            await msg.answer("Какой вам нужен город?", reply_markup=kb)
        else:
            city = user_cities[0]
    elif isinstance(msg, types.CallbackQuery):
        await bot.answer_callback_query(msg.id)
        city = msg.data.split("=")[-1]
    if city:
        async with state.proxy() as data:
            data["city"] = city
        await BotStates.ADDRESS.set()
        await bot.send_message(msg.from_user.id, "Какой адрес интересует?")


# @dp.callback_query_handler(
#     lambda c: parse_callback_data(c.data).get("url") == "MAP_MENU"
#     and parse_callback_data(c.data).get("B_C")
# )
# @dp.message_handler(commands=["test"], user_have_rights=Rights.GET_MAP)
# async def map_menu_handler(msg: Union[types.Message, types.CallbackQuery]):
#     user_cities = Users.get_user_cities(msg.from_user.id)
#     if len(user_cities) == 0:
#         await msg.answer("Вот дерьмо, у вас не задан город")
#     elif len(user_cities) > 1:
#         kb = types.InlineKeyboardMarkup().add(
#             *list(
#                 map(
#                     lambda city: types.InlineKeyboardButton(
#                         city, callback_data=f"MAP_MENU&CH_C&C={city.replace(' ', '_')}"
#                     ),
#                     user_cities,
#                 )
#             )
#         )

#         if isinstance(msg, types.Message):
#             await msg.answer("Выберите город, где нужна карта", reply_markup=kb)
#         else:
#             await bot.edit_message_text(
#                 text="Выберите город, где нужна карта",
#                 chat_id=msg.message.chat.id,
#                 message_id=msg.message.message_id,
#                 reply_markup=kb,
#             )
#     else:
#         callback = types.CallbackQuery()
#         callback.data = f"MAP_MENU&C={user_cities[0]}"
#         callback["message"] = {"chat": {}}
#         callback["message"]["chat"]["id"] = msg.chat.id
#         callback["message"]["message_id"] = msg.message_id
#         await region_choose_handler(callback)


# @dp.callback_query_handler(
#     lambda c: parse_callback_data(c.data).get("url") == "MAP_MENU"
#     and parse_callback_data(c.data).get("B_R")
# )
# @dp.callback_query_handler(
#     lambda c: parse_callback_data(c.data).get("url") == "MAP_MENU"
#     and parse_callback_data(c.data).get("CH_C")
# )
# async def region_choose_handler(msg: types.CallbackQuery):
#     city = parse_callback_data(msg.data).get("C").replace("_", " ")
#     if parse_callback_data(msg.data).get("CH_C") or parse_callback_data(msg.data).get(
#         "B_R"
#     ):
#         await bot.answer_callback_query(msg.id)
#     kb = types.InlineKeyboardMarkup().add(
#         *(
#             list(
#                 map(
#                     lambda region: types.InlineKeyboardButton(
#                         region.name,
#                         callback_data=f"MAP_MENU&CH_R&C={city.replace(' ', '_')}&REG={region.name}",
#                     ),
#                     db.get_regions(city),
#                 )
#             )
#             + [types.InlineKeyboardButton("! Назад", callback_data="MAP_MENU&B_C")]
#         )
#     )

#     if not parse_callback_data(msg.data).get("CH_C") and not parse_callback_data(
#         msg.data
#     ).get("B_R"):
#         await bot.send_message(
#             chat_id=msg.message.chat.id,
#             text=f"Выберите регион города {city}",
#             reply_markup=kb,
#         )

#     else:
#         await bot.edit_message_text(
#             chat_id=msg.message.chat.id,
#             message_id=msg.message.message_id,
#             text=f"Выберите регион города {city}",
#             reply_markup=kb,
#         )


# @dp.callback_query_handler(
#     lambda c: parse_callback_data(c.data).get("url") == "MAP_MENU"
#     and parse_callback_data(c.data).get("CH_R")
# )
# async def map_select_handler(msg: types.CallbackQuery):
#     await bot.answer_callback_query(msg.id)
#     city = parse_callback_data(msg.data).get("C").replace("_", " ")
#     region = parse_callback_data(msg.data).get("REG")
#     maps = db.get_maps(city, region)
#     kb = types.InlineKeyboardMarkup().add(
#         *list(
#             map(
#                 lambda mp: types.InlineKeyboardButton(
#                     mp.name,
#                     callback_data=f"MAP_MENU&CH_M&C={city.replace(' ', '_')}&M={mp.name}",
#                 ),
#                 maps,
#             )
#         )
#         + [
#             types.InlineKeyboardButton(
#                 "! Назад", callback_data=f"MAP_MENU&B_R&C={city.replace(' ', '_')}"
#             )
#         ]
#     )
#     await bot.edit_message_text(
#         chat_id=msg.message.chat.id,
#         message_id=msg.message.message_id,
#         text="Какую карту хотите?",
#         reply_markup=kb,
#     )
