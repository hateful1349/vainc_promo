from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import bot, dp
from states.states import BotStates
from utils.callback import parse_callback_data
from utils.users import Rights, Users


@dp.callback_query_handler(lambda c: parse_callback_data(c.data).get("url") == "RIGHTS")
@dp.message_handler(
    text=Rights.comments.get(Rights.CHANGE_USER_PERMISSIONS),
    user_have_rights=[Rights.CHANGE_USER_PERMISSIONS],
)
async def test(msg: Union[types.Message, types.CallbackQuery]):
    menu = (
        "START"
        if isinstance(msg, types.Message)
        else parse_callback_data(msg.data).get("MENU") or "START"
    )
    print("CURRENT_MENU:", menu)
    chosen_user = None
    if isinstance(msg, types.CallbackQuery):
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
                    lambda user: types.InlineKeyboardButton(
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
                types.KeyboardButton(
                    "🏙️ Город",
                    callback_data=f"RIGHTS&MENU=CHANGE_CITY&USER={chosen_user}",
                ),
                types.KeyboardButton(
                    "🔑 Права",
                    callback_data=f"RIGHTS&MENU=CHANGE_RIGHTS&USER={chosen_user}",
                ),
                types.KeyboardButton(
                    "💾 Данные",
                    callback_data=f"RIGHTS&MENU=CHANGE_DATA&USER={chosen_user}",
                ),
                types.KeyboardButton(
                    "💾 Начальство",
                    callback_data=f"RIGHTS&MENU=CHANGE_MANAGERS&USER={chosen_user}",
                ),
                types.KeyboardButton("🔙 Назад", callback_data="RIGHTS"),
            ],
        },
    }

    if isinstance(msg, types.Message):
        await msg.answer(
            menus.get(menu).get("text"),
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                *menus.get(menu).get("buttons")
            ),
        )
    else:
        await bot.answer_callback_query(msg.id)
        await bot.edit_message_text(
            chat_id=msg.message.chat.id,
            message_id=msg.message.message_id,
            text=menus.get(menu).get("text"),
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                *menus.get(menu).get("buttons")
            ),
        )


# @dp.message_handler(state=BotStates.WAIT_FOR_CITY_RESOURCES, content_types=["document"])
async def get_city_resources(msg: types.Document, state: FSMContext = None):
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


@dp.message_handler(
    text=Rights.comments.get(Rights.CITY_MANAGEMENT),
    user_have_rights=[Rights.CITY_MANAGEMENT],
)
async def change_city(msg: types.Message):
    await msg.answer("Тут ща будет добавление нового города")
    await msg.answer(
        "Отправь мне в одном сообщении zip архив с картами и xlsx таблицу с адресами \(не работает пока, поэтому не пытайся\)"
    )
    # await BotStates.WAIT_FOR_CITY_RESOURCES.set()
