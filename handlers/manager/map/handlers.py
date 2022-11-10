from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from database.database import Database
from database.users import Rights, Users
from handlers.manager.map.map_sender import send_map
from loader import bot, dp
from states.states import BotStates


# ? SIMPLE TEXT HANDLERS

@dp.message_handler(
    Text(equals=Rights.comments.get(Rights.GET_MAP)),
    user_have_rights=Rights.GET_MAP,
    state="*",
)
@dp.message_handler(commands=["map"], user_have_rights=Rights.GET_MAP, state="*")
async def map_handler(msg: types.Message, state: FSMContext):
    user_cities = Users.get_cities(msg.from_user.id)
    match user_cities:
        case []:
            await msg.answer(
                "⚠️ У вас не задан город\nОбратитесь к вышестоящему лицу за подробностями"
            )
            return
        case [city]:
            await BotStates.WAIT_FOR_MAP.set()

            async with state.proxy() as data:
                data["city"] = city.name

            regions = Database.get_regions(city.name)
            kb = types.InlineKeyboardMarkup().add(
                *list(
                    map(
                        lambda region: types.InlineKeyboardButton(
                            region.name, callback_data=f"reg={region.name}"
                        ),
                        sorted(regions, key=lambda reg: reg.name),
                    )
                )
            )

            await msg.answer(
                f"Выбран город - {city.name}",
                reply_markup=kb,
            )
        case [*_]:
            kb = types.InlineKeyboardMarkup().add(
                *list(
                    map(
                        lambda city: types.InlineKeyboardButton(
                            city.name,
                            callback_data=f"{city.name}",
                        ),
                        sorted(user_cities, key=lambda c: c.name),
                    )
                )
            )
            new_msg = await msg.answer("Какой вам нужен город?", reply_markup=kb)
            await BotStates.WAIT_FOR_MAP_CITY.set()
            async with state.proxy() as data:
                data["msg_edit_id"] = {
                    "chat_id": msg.chat.id,
                    "msg_id": new_msg.message_id,
                }

# TODO убрать нахер этот костыль и сделать нормальную регистрацию хендлеров
@dp.message_handler(
    Text(equals=Rights.comments.get(Rights.GET_ADDRESS)),
    user_have_rights=Rights.GET_ADDRESS,
    state="*"
)
async def address_handler(msg: types.Message, state: FSMContext):
    user_cities = Users.get_cities(msg.from_user.id)
    match user_cities:
        case []:
            await msg.answer(
                "⚠️ У вас не задан город\nОбратитесь к вышестоящему лицу за подробностями"
            )
            return
        case [city]:
            await BotStates.WAIT_FOR_ADDRESS.set()

            async with state.proxy() as data:
                data["city"] = city.name

            await msg.answer(
                f"Выбран город - {city.name}\nЧто искать будем?",
            )
        case [*_]:
            kb = types.InlineKeyboardMarkup().add(
                *list(
                    map(
                        lambda c: types.InlineKeyboardButton(
                            c.name,
                            callback_data=f"{c.name}",
                        ),
                        sorted(user_cities, key=lambda c: c.name),
                    )
                )
            )
            new_msg = await msg.answer("Какой вам нужен город?", reply_markup=kb)
            await BotStates.WAIT_FOR_ADDRESS_CITY.set()
            async with state.proxy() as data:
                data["msg_edit_id"] = {
                    "chat_id": msg.chat.id,
                    "msg_id": new_msg.message_id,
                }


# TODO убрать нахер этот костыль и сделать нормальную регистрацию хендлеров
@dp.message_handler(
    Text(equals=Rights.comments.get(Rights.CHANGE_USER_PERMISSIONS)),
    user_have_rights=Rights.CHANGE_USER_PERMISSIONS,
    state="*"
)
async def main_menu_handler(msg: types.Message, state: FSMContext):
    # user = Users.get_user(msg.from_user.id)

    kb = types.InlineKeyboardMarkup().add(
        *list(
            map(
                lambda u: types.InlineKeyboardButton(
                    Users.get_readable_name(u),
                    callback_data=f"user_menu&{u.tg_id}",
                ),
                sorted(Users.get_slaves(msg.from_user.id), key=lambda u: u.id)
            )
        )
         + [types.InlineKeyboardButton("➕ Новый юзер", callback_data="new_user")]
    )
    await msg.answer("Кого покараем/наградим?", reply_markup=kb)
    await BotStates.USER_RIGHTS.set()


# TODO убрать нахер этот костыль и сделать нормальную регистрацию хендлеров
@dp.message_handler(
    Text(equals=Rights.comments.get(Rights.CITY_MANAGEMENT)),
    user_have_rights=Rights.CITY_MANAGEMENT,
    state="*"
)
async def city_management_handler(msg: types.Message, state: FSMContext):
    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("Новый", callback_data="new_city"),
            types.KeyboardButton("Изменить", callback_data="edit_city"),
            types.KeyboardButton("Удалить", callback_data="remove_city"),
        ]
    )

    await msg.answer("Что именно вы хотите сделать с городами?", reply_markup=kb)
    await BotStates.FILES.set()


@dp.message_handler(state=BotStates.WAIT_FOR_MAP)
async def wait_for_map_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        city = data["city"]

    request = msg.text.lower().split()

    for map_name in request:
        await send_map(msg.from_user.id, city, map_name=map_name)


@dp.message_handler(state=BotStates.WAIT_FOR_MAP_CITY)
async def wait_for_city_handler(msg: types.Message, state: FSMContext):
    request = msg.text.lower()

    city = list(set(map(lambda city: city.name, Database.get_cities())) & {request})
    if not city:
        await msg.answer("Я не знаю такого города")
        return
    city = city[0]

    await BotStates.WAIT_FOR_MAP.set()

    async with state.proxy() as data:
        data["city"] = request

    async with state.proxy() as data:
        msg_id = data["msg_edit_id"]["msg_id"]
        chat_id = data["msg_edit_id"]["chat_id"]
    regions = Database.get_regions(city)
    kb = types.InlineKeyboardMarkup().add(
        *list(
            map(
                lambda region: types.InlineKeyboardButton(
                    region.name, callback_data=f"reg={region.name}"
                ),
                sorted(regions, key=lambda reg: reg.name),
            )
        )
    )
    await bot.edit_message_text(
        f"Выбран город - {city.title()}",
        chat_id,
        msg_id,
        reply_markup=kb,
    )


# ? CALLBACKS


@dp.callback_query_handler(state=BotStates.WAIT_FOR_MAP_CITY)
async def wait_for_city_callback(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data
    await bot.answer_callback_query(callback.id)
    await BotStates.WAIT_FOR_MAP.set()

    async with state.proxy() as data:
        data["city"] = city

    regions = Database.get_regions(city)
    kb = types.InlineKeyboardMarkup().add(
        *list(
            map(
                lambda region: types.InlineKeyboardButton(
                    region.name, callback_data=f"reg={region.name}"
                ),
                sorted(regions, key=lambda reg: reg.name),
            )
        )
    )
    await bot.edit_message_text(
        f"Выбран город - {city.title()}",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(
    lambda callback: callback.data.startswith("reg"), state=BotStates.WAIT_FOR_MAP
)
async def region_choose_callback(callback: types.CallbackQuery, state: FSMContext):
    region = callback.data.lower().strip("reg=")
    async with state.proxy() as data:
        city = data.get("city")
    await bot.answer_callback_query(callback.id)
    maps = Database.get_maps(city, region)

    kb = types.InlineKeyboardMarkup().add(
        *list(
            map(
                lambda mp: types.InlineKeyboardButton(
                    mp.name, callback_data=f"map_{mp.id}"
                ),
                sorted(maps, key=lambda mp: mp.name),
            )
        )
    )

    await bot.edit_message_text(
        f"Выбран город - {city}",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(
    lambda callback: callback.data.startswith("map_"), state=[BotStates.WAIT_FOR_MAP, BotStates.WAIT_FOR_ADDRESS]
)
async def wait_for_map_callback(callback: types.CallbackQuery, state: FSMContext):
    request = callback.data.lower()
    async with state.proxy() as data:
        city = data["city"]

    await bot.answer_callback_query(callback.id)
    if request.startswith("map"):
        map_id = request.split("_")[-1]
        await send_map(callback.message.chat.id, city, map_id=map_id)
    else:
        await send_map(callback.message.chat.id, city, map_name=request)
