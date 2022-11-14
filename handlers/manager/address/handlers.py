import difflib

from aiogram import types
from aiogram.dispatcher import FSMContext

from database.database import Database
from handlers.manager.map.map_sender import send_map
from loader import bot, dp, config
from states.states import BotStates


@dp.message_handler(state=BotStates.WAIT_FOR_ADDRESS)
async def wait_for_address(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        city_name = data["city"]
    request = msg.text

    if matches_map := Database.get_matches_map(request, city_name):
        await send_map(msg.from_user.id, map_obj=matches_map)
    else:
        addresses = Database.get_addresses(city_name)
        closest_addresses_names: list[str] = (
            difflib.get_close_matches(
                request,
                list(
                    map(
                        lambda address: (
                            (address.street or '')
                            + ' '
                            + (address.number or '')
                        ),
                        addresses
                    )
                ),
                n=config.address_search_count)
        )

        closest_maps = [Database.get_matches_map(address, city_name) for address in closest_addresses_names]
        for address, map_obj in zip(closest_addresses_names, closest_maps):
            kb = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(
                    map_obj.name,
                    callback_data=f"map_{map_obj.id}"
                )
            )
            await msg.answer(address, reply_markup=kb)
        # await BotStates.WAIT_FOR_MAP.set()


@dp.message_handler(state=BotStates.WAIT_FOR_ADDRESS_CITY)
async def wait_for_city_handler(msg: types.Message, state: FSMContext):
    request = msg.text

    city = list(set(map(lambda city_obj: city_obj.name, Database.get_cities())) & {request})
    if not city:
        await msg.answer("Я не знаю такого города")
        return
    city = city[0]

    await BotStates.WAIT_FOR_ADDRESS.set()

    async with state.proxy() as data:
        data["city"] = request

    async with state.proxy() as data:
        msg_id = data["msg_edit_id"]["msg_id"]
        chat_id = data["msg_edit_id"]["chat_id"]
    await bot.edit_message_text(
        f"Выбран город - {city}\nЧто искать будем?",
        chat_id,
        msg_id,
    )


@dp.callback_query_handler(state=BotStates.WAIT_FOR_ADDRESS_CITY)
async def wait_for_city_callback(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data
    await bot.answer_callback_query(callback.id)
    await BotStates.WAIT_FOR_ADDRESS.set()

    async with state.proxy() as data:
        data["city"] = city

    await bot.edit_message_text(
        f"Выбран город - {city}\nЧто искать будем?",
        callback.message.chat.id,
        callback.message.message_id,
    )
