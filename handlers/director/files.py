import contextlib
import os
import shutil

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentTypes
from aiogram.utils import exceptions

from database.database import Database
# from database.users import Rights
from loader import bot, dp
from states.states import BotStates
from utils.helpers import join_file_parts


# @dp.message_handler(
#     Text(equals=Rights.comments.get(Rights.CITY_MANAGEMENT)),
#     user_have_rights=Rights.CITY_MANAGEMENT,
#     state="*"
# )
# async def city_management_handler(msg: types.Message):
#     kb = types.InlineKeyboardMarkup(row_width=1).add(
#         *[
#             types.KeyboardButton("Новый", callback_data="new_city"),
#             types.KeyboardButton("Изменить", callback_data="edit_city"),
#             types.KeyboardButton("Удалить", callback_data="remove_city"),
#         ]
#     )
#
#     await msg.answer("Что именно вы хотите сделать с городами?", reply_markup=kb)


@dp.callback_query_handler(lambda callback: callback.data == "new_city", state=BotStates.FILES)
async def new_city_callback(callback: types.CallbackQuery):
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(f"{os.curdir}/.cache")
    await bot.answer_callback_query(callback.id)

    await bot.edit_message_text(
        "Как будет зваться новый город?",
        callback.message.chat.id,
        callback.message.message_id,
    )
    await BotStates.WAIT_FOR_CITY_NAME.set()


@dp.message_handler(state=BotStates.WAIT_FOR_CITY_NAME)
async def wait_city_name_handler(msg: types.Message, state: FSMContext):
    city_name = msg.text

    await BotStates.WAIT_FOR_CITY_XLSX.set()

    async with state.proxy() as data:
        data["city_name"] = city_name

    await msg.answer("Отлично!")
    await msg.answer(f"Теперь отправьте мне xlsx-файл с данными по городу {city_name}")
    await msg.answer("Если ошиблись, то можете написать /cancel и повторить заново")


@dp.message_handler(
    state=BotStates.WAIT_FOR_CITY_XLSX, content_types=ContentTypes.DOCUMENT
)
async def xlsx_get_handler(msg: types.Message, state: FSMContext):
    if document := msg.document:
        await msg.answer("Скачиваю...")

        async with state.proxy() as data:
            city_name = data["city_name"]

        xlsx_file_path = f"{os.curdir}/.cache/{city_name}.xlsx"
        await document.download(
            timeout=180, destination_file=xlsx_file_path, make_dirs=True
        )

        await BotStates.WAIT_FOR_CITY_ZIP.set()

        async with state.proxy() as data:
            data["city_name"] = city_name
            data["xlsx_path"] = xlsx_file_path

        await msg.answer("Скачал!")
        await msg.answer(f"Теперь я жду от вас zip-архив с картами для {city_name}")

        kb = types.InlineKeyboardMarkup(row_width=2).add(
            *[
                types.KeyboardButton("Да", callback_data="big_size_zip"),
                types.KeyboardButton("Нет", callback_data="common_zip"),
            ]
        )
        await msg.answer("Размер вашего архива больше 20МБ?", reply_markup=kb)


@dp.callback_query_handler(
    lambda callback: callback.data == "common_zip", state=BotStates.WAIT_FOR_CITY_ZIP
)
async def common_size_zip_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    await bot.edit_message_text(
        "Жду...",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )


@dp.callback_query_handler(
    lambda callback: callback.data == "big_size_zip", state=BotStates.WAIT_FOR_CITY_ZIP
)
async def big_size_zip_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="Telegram API не позволяет мне скачивать файлы размером больше 20МБ, "
             "поэтому вам необходимо разделить ваш архив, "
             "используя WinRAR для Windows или команду split для Linux (split -b 'размер частей' "
             "'название исходного архива' 'префикс для результирующих частей') (split -b 20M Омск.zip Омск.zip.)",
    )
    await bot.send_message(
        text="Затем отправьте мне фрагменты вашего разбитого архива",
        chat_id=callback.message.chat.id,
    )
    await bot.send_message(
        text="Когда все части будут загружены, "
             "необходимо нажать на кнопку ниже, "
             "что вы закончили",
        chat_id=callback.message.chat.id,
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
            types.KeyboardButton("Весь архив")
        ),
    )

    async with state.proxy() as data:
        city_name = data["city_name"]
        xlsx_file_path = data["xlsx_path"]

    await BotStates.WAIT_FOR_CITY_BIG_ZIP.set()

    async with state.proxy() as data:
        data["city_name"] = city_name
        data["xlsx_path"] = xlsx_file_path


@dp.message_handler(
    state=BotStates.WAIT_FOR_CITY_ZIP, content_types=ContentTypes.DOCUMENT
)
async def zip_get_handler(msg: types.Message, state: FSMContext):
    if document := msg.document:
        await msg.answer("Скачиваю...")

        async with state.proxy() as data:
            city_name = data["city_name"]
            xlsx_file_path = data["xlsx_path"]

        zip_file_file_path = f"{os.curdir}/.cache/{city_name}.zip"
        try:
            await document.download(
                timeout=180, destination_file=zip_file_file_path, make_dirs=True
            )

            await msg.answer("Скачал!")

            await msg.answer("Хорошо, сейчас подождите немного, пока я это обработаю")
            await msg.answer("Я отпишусь, когда закончу")

            # Database.create_city(city_name, zip_file_file_path, xlsx_file_path)

            await msg.answer("Готово!")

            await dp.current_state(user=msg.from_user.id).reset_state()
        except exceptions.FileIsTooBig:
            await msg.answer("Архив слишком большой (>20МБ)")
            await msg.answer(
                "Это ограничение telegram-api, я ничего не могу с этим сделать"
            )
            await msg.answer(
                "Пожалуйста разделите файл на части по 20МБ\n"
                "Затем отправьте мне разделенный по частям архив\n"
                "Когда закончите, нажмите кнопку внизу",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton("Весь архив")
                ),
            )
            await msg.answer(
                "Для разделения архива на части вы можете воспользоваться WinRAR для Windows или командой "
                "split в Linux"
            )

            await BotStates.WAIT_FOR_CITY_BIG_ZIP.set()

            async with state.proxy() as data:
                data["city_name"] = city_name
                data["xlsx_path"] = xlsx_file_path


@dp.message_handler(
    state=BotStates.WAIT_FOR_CITY_BIG_ZIP, content_types=ContentTypes.DOCUMENT
)
async def zip_part_handler(msg: types.Message, state: FSMContext):
    if document := msg.document:
        await msg.answer("Скачиваю...")

        async with state.proxy() as data:
            city_name = data["city_name"]
            part_index = data.get("part_index") or 0

        part_zip_dir_path = f"{os.curdir}/.cache/"

        try:
            await document.download(
                timeout=180, destination_dir=part_zip_dir_path, make_dirs=True
            )

            await msg.answer(f"Скачал! ({part_index})")

            async with state.proxy() as data:
                data["part_index"] = part_index + 1
        except exceptions.FileIsTooBig:
            await msg.answer("Файл слишком больльной, попробуй ещё раз")


@dp.message_handler(commands=["test"])
@dp.message_handler(
    Text(equals="Весь архив"),
    state=BotStates.WAIT_FOR_CITY_BIG_ZIP,
    content_types=ContentTypes.TEXT,
)
async def zip_part_end_handler(msg: types.Message, state: FSMContext):
    await msg.answer("Обработка...")
    await msg.answer("Подождите, пожалуйста (минуту)")

    async with state.proxy() as data:
        city_name = data.get("city_name")
        xlsx_file_path = data.get("xlsx_path")

    zip_file_path = f"{os.curdir}/.cache/{city_name}.zip"

    join_file_parts(
        f"{os.curdir}/.cache/documents", file_to_write=zip_file_path, echo=True
    )

    Database.create_city(city_name, zip_file_path, xlsx_file_path)

    await msg.answer("Я закончил!")
    await dp.current_state(user=msg.from_user.id).reset_state()


@dp.callback_query_handler(lambda callback: callback.data == "remove_city", state=BotStates.FILES)
async def remove_city_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    cities = Database.get_cities()

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda city: types.KeyboardButton(
                    city.name.capitalize(), callback_data=f"remove_city&{city.id}"
                ),
                cities,
            )
        )
    )

    await bot.edit_message_text(
        "Какой город удалить?",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith("remove_city"), state=BotStates.FILES)
async def remove_city_arg_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    city_id = int(callback.data.split("&")[1])

    await bot.send_message(callback.message.chat.id, "Удалил")

    Database.delete_city(city_id)

    await bot.send_message(callback.message.chat.id, "Удаляю")

# TODO update_city_resources()
