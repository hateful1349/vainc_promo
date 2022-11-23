from aiogram import types
from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text

from database.database import Database
from database.users import Rights, Users
from keyboards.inline import simple_kb
from loader import bot, dp
from states.states import BotStates
from utils.messages.messages import Messages


# @dp.message_handler(
#     Text(equals=Rights.comments.get(Rights.CHANGE_USER_PERMISSIONS)),
#     user_have_rights=Rights.CHANGE_USER_PERMISSIONS,
#     state="*"
# )
# async def main_menu_handler(msg: types.Message):
#     # user = Users.get_user(msg.from_user.id)
#
#     kb = types.InlineKeyboardMarkup().add(
#         *list(
#             map(
#                 lambda u: types.InlineKeyboardButton(
#                     Users.get_readable_name(u),
#                     callback_data=f"user_menu&{u.tg_id}",
#                 ),
#                 Users.get_slaves(msg.from_user.id)
#             )
#         )
#          + [types.InlineKeyboardButton("➕ Новый юзер", callback_data="new_user")]
#     )
#     await msg.answer("Кого покараем/наградим?", reply_markup=kb)


@dp.callback_query_handler(lambda callback: callback.data == "main_menu", state=BotStates.USER_RIGHTS)
async def main_menu_callback(callback: types.CallbackQuery):
    # kb = types.InlineKeyboardMarkup().add(
    #     *list(
    #         map(
    #             lambda u: types.InlineKeyboardButton(
    #                 Users.get_readable_name(u),
    #                 callback_data=f"user_menu&{u.tg_id}",
    #             ),
    #             sorted(Users.get_slaves(callback.from_user.id), key=lambda u: u.id)
    #         )
    #     ) + [types.InlineKeyboardButton(Messages.users_new_user_btn, callback_data="new_user")]
    # )

    kb = simple_kb(
        {
            Users.get_readable_name(u): f"user_menu&{u.tg_id}"
            for u in sorted(Users.get_slaves(callback.from_user.id), key=lambda u: u.id)
        }
    )
    kb.add(types.InlineKeyboardButton(Messages.users_new_user_btn, callback_data="new_user"))

    await bot.edit_message_text(
        "Кого покараем/наградим?",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


# get new user
@dp.callback_query_handler(lambda callback: callback.data == "new_user", state=BotStates.USER_RIGHTS)
async def new_user_callback(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        "Дайте мне id нового пользователя",
        callback.message.chat.id,
        callback.message.message_id,
    )
    await BotStates.WAIT_FOR_USER_ID.set()


@dp.message_handler(state=BotStates.WAIT_FOR_USER_ID)
async def new_user_message(msg: types.Message, state: FSMContext):
    user_id = msg.text
    Users.new_user(user_id)
    Users.add_manager(user_id, msg.from_user.id)

    kb = types.InlineKeyboardMarkup().add(
        *[
            types.KeyboardButton("🔙 Назад", callback_data="main_menu"),
        ]
    )
    await msg.answer(f"Пользователь с id: {user_id} добавлен", reply_markup=kb)
    await dp.current_state(user=msg.from_user.id).reset_state()
    await BotStates.USER_RIGHTS.set()


####
@dp.callback_query_handler(lambda callback: callback.data.startswith("user_menu"), state=BotStates.USER_RIGHTS)
async def user_menu_callback(callback: types.CallbackQuery, state: FSMContext):
    chosen_user = callback.data.split("&")[1]
    async with state.proxy() as data:
        data["chosen_user"] = chosen_user

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("🏙️ Город", callback_data="user_cities"),
            types.KeyboardButton("🔑 Права", callback_data="user_rights"),
            types.KeyboardButton("💾 Данные", callback_data="user_data"),
            types.KeyboardButton("💼 Начальство", callback_data="user_managers")
        ])
    if Users.get_user(callback.from_user.id).superuser:
        kb.add(types.KeyboardButton(f"👑 Суперюзер ({'✔️' if Users.get_user(chosen_user).superuser else '✖️'})",
                                    callback_data="user_super"))
    kb.add(*[
        types.KeyboardButton(
            "❌ Удалить нахер", callback_data=f"del_user&{chosen_user}"
        ),
        types.KeyboardButton("🔙 Назад", callback_data="main_menu"),
    ]
           )

    await bot.edit_message_text(
        Users.get_readable_info(chosen_user),
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data == "user_super", state=BotStates.USER_RIGHTS)
async def user_super_toggle_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.toggle_super(user_id)
    user = Users.get_user(user_id)

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("🏙️ Город", callback_data="user_cities"),
            types.KeyboardButton("🔑 Права", callback_data="user_rights"),
            types.KeyboardButton("💾 Данные", callback_data="user_data"),
            types.KeyboardButton("💼 Начальство", callback_data="user_managers")
        ])
    if Users.get_user(callback.from_user.id).superuser:
        kb.add(types.KeyboardButton(f"👑 Суперюзер ({'✔️' if user.superuser else '✖️'})",
                                    callback_data="user_super"))
    kb.add(*[
        types.KeyboardButton(
            "❌ Удалить нахер", callback_data=f"del_user&{user.tg_id}"
        ),
        types.KeyboardButton("🔙 Назад", callback_data="main_menu"),
    ]
           )

    await bot.edit_message_text(
        Users.get_readable_info(user.tg_id),
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


# НАЧАЛЬСТВО

@dp.callback_query_handler(lambda callback: callback.data == "user_managers", state=BotStates.USER_RIGHTS)
async def user_rights_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    user_masters = Users.get_masters(user_id)
    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("➕ Начальник", callback_data="add_manager"),
            types.KeyboardButton("➖ Начальник", callback_data="del_manager"),
            types.KeyboardButton("🔙 Назад", callback_data=f"user_menu&{user_id}"),
        ]
    )

    masters_txt = [Users.get_readable_name(u) for u in user_masters]

    await bot.edit_message_text(
        ", ".join(masters_txt) or "Нет начальников",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data == "add_manager", state=BotStates.USER_RIGHTS)
async def add_right_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    users = Users.get_users()
    users_map = {user.id: user for user in users}
    not_masters = set(map(lambda u: u.id, users)) - {Users.get_user(callback.from_user.id).id} - set(
        map(lambda u: u.id, Users.get_masters(user_id))) - set(map(lambda u: u.id, Users.get_slaves(user_id))) - {
                      Users.get_user(user_id).id}

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda u_id: types.KeyboardButton(Users.get_readable_name(users_map[u_id]),
                                                  callback_data=f"add_manager&{users_map[u_id].tg_id}"),
                # all_users - self - user_masters - user_slaves - user
                sorted(not_masters)
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_managers")]
    )

    await bot.edit_message_text(
        "Чьей сучкой будет?\n(Возможные начальники это все, кроме вас, его начальников, его подчиненных и его самого)",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith("add_manager"), state=BotStates.USER_RIGHTS)
async def add_right_arg_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    master_user_id = callback.data.split("&")[1]

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.add_manager(user_id, master_user_id)

    user_masters = Users.get_masters(user_id)

    users = Users.get_users()
    users_map = {user.id: user for user in users}
    not_masters = set(map(lambda u: u.id, users)) - {Users.get_user(callback.from_user.id).id} - set(
        map(lambda u: u.id, user_masters)) - set(map(lambda u: u.id, Users.get_slaves(user_id))) - {
                      Users.get_user(user_id).id}

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda u_id: types.KeyboardButton(Users.get_readable_name(users_map[u_id]),
                                                  callback_data=f"add_manager&{users_map[u_id].tg_id}"),
                sorted(not_masters)
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_managers")]
    )

    masters_txt = [Users.get_readable_name(u) for u in user_masters]

    await bot.edit_message_text(
        ", ".join(masters_txt) or "Нет начальников",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data == "del_manager", state=BotStates.USER_RIGHTS)
async def del_right_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    users = Users.get_users()
    users_map = {user.id: user for user in users}
    masters = set(map(lambda u: u.id, Users.get_masters(user_id))) - {Users.get_user(callback.from_user.id).id} - set(
        map(lambda u: u.id, Users.get_masters(callback.from_user.id)))
    # user_masters - self - self_masters

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda u_id: types.KeyboardButton(Users.get_readable_name(users_map[u_id]),
                                                  callback_data=f"del_manager&{users_map[u_id].tg_id}"),
                sorted(masters)
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_managers")]
    )

    await bot.edit_message_text(
        "Кого из начальников уберем у него?\n"
        "(Убрать можно только тех, кто не в списке ваших начальников и нельзя убрать вас)",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith("del_manager"), state=BotStates.USER_RIGHTS)
async def del_right_arg_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    master_user_id = callback.data.split("&")[1]

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.del_manager(user_id, master_user_id)

    users = Users.get_users()
    users_map = {user.id: user for user in users}
    user_masters = Users.get_masters(user_id)
    masters = set(map(lambda u: u.id, user_masters)) - {Users.get_user(callback.from_user.id).id} - set(
        map(lambda u: u.id, Users.get_masters(callback.from_user.id)))
    # user_masters - self - self_masters

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda u_id: types.KeyboardButton(Users.get_readable_name(users_map[u_id]),
                                                  callback_data=f"del_manager&{users_map[u_id].tg_id}"),
                sorted(masters)
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_managers")]
    )

    masters_txt = [Users.get_readable_name(u) for u in user_masters]

    await bot.edit_message_text(
        ", ".join(masters_txt),
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


#############


@dp.callback_query_handler(lambda callback: callback.data.startswith("del_user"), state=BotStates.USER_RIGHTS)
async def delete_user_arg_callback(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)

    user_id = callback.data.split("&")[1]

    Users.del_user(tg_id=user_id)

    await bot.edit_message_text(
        "Удален",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.KeyboardButton("🔙 Назад", callback_data="main_menu"),
        ),
    )


# CITY MANIPULATING


@dp.callback_query_handler(lambda callback: callback.data == "user_cities", state=BotStates.USER_RIGHTS)
async def user_cities_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    user_cities = Users.get_cities(user_id)
    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("➕ Назначить", callback_data="add_city"),
            types.KeyboardButton("➖ Забрать", callback_data="del_city"),
            types.KeyboardButton("🔙 Назад", callback_data=f"user_menu&{user_id}"),
        ]
    )
    await bot.edit_message_text(
        ", ".join(list(map(lambda city: city.name, user_cities))) or "Город не задан",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


# CITY ADD


@dp.callback_query_handler(lambda callback: callback.data == "add_city", state=BotStates.USER_RIGHTS)
async def add_city_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    user_cities = Users.get_cities(user_id)

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda c: types.KeyboardButton(
                    c, callback_data=f"add_city&{c}"
                ),
                sorted(set(map(lambda c: c.name, Database.get_cities())) - set(map(lambda c: c.name, user_cities)))
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_cities")]
    )
    await bot.edit_message_text(
        "Какой город ему добавим?",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith("add_city"), state=BotStates.USER_RIGHTS)
async def add_city_arg_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    city = callback.data.split("&")[1]

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.add_city(user_id, city)

    user_cities = Users.get_cities(user_id)

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda c: types.KeyboardButton(
                    c, callback_data=f"add_city&{c}"
                ),
                sorted(set(map(lambda c: c.name, Database.get_cities())) - set(map(lambda c: c.name, user_cities)))
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_cities")]
    )

    await bot.edit_message_text(
        (", ".join(list(map(lambda c: c.name, user_cities)))) + f"\nГород {city} добавлен",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


#####

# CITY DELETE


@dp.callback_query_handler(lambda callback: callback.data == "del_city", state=BotStates.USER_RIGHTS)
async def del_city_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *(
                list(
                    map(
                        lambda city: types.KeyboardButton(
                            city.name, callback_data=f"del_city&{city.name}"
                        ),
                        sorted(Users.get_cities(user_id), key=lambda c: c.name),
                    )
                )
                + [types.KeyboardButton("🔙 Назад", callback_data="user_cities")]
        )
    )

    await bot.edit_message_text(
        "Какой город отберем?",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith("del_city"), state=BotStates.USER_RIGHTS)
async def del_city_arg_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    city_name = callback.data.split("&")[1]

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.del_city(user_id, city_name)

    user_cities = Users.get_cities(user_id)

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *(
                list(
                    map(
                        lambda c: types.KeyboardButton(
                            c.name, callback_data=f"del_city&{c.name}"
                        ),
                        sorted(user_cities, key=lambda c: c.name),
                    )
                )
                + [types.KeyboardButton("🔙 Назад", callback_data="user_cities")]
        )
    )

    await bot.edit_message_text(
        (", ".join(list(map(lambda city: city.name, user_cities))) or "Город не задан") + f"\nГород {city_name} удален",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


#####


@dp.callback_query_handler(lambda callback: callback.data == "user_rights", state=BotStates.USER_RIGHTS)
async def user_rights_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

        user_rights = Users.get_user_rights(user_id)
        kb = types.InlineKeyboardMarkup(row_width=1).add(
            *[
                types.KeyboardButton("➕ Права", callback_data="add_right"),
                types.KeyboardButton("➖ Права", callback_data="del_right"),
                types.KeyboardButton("🔙 Назад", callback_data=f"user_menu&{user_id}"),
            ]
        )

        await bot.edit_message_text(
            ", ".join(list(map(lambda r: r.name, user_rights))) or "Нет прав",
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=kb,
        )


@dp.callback_query_handler(lambda callback: callback.data == "add_right", state=BotStates.USER_RIGHTS)
async def add_right_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda r: types.KeyboardButton(r, callback_data=f"add_right&{r}"),
                sorted(set(Rights.comments.keys()) - set(map(lambda r: r.name, Users.get_user_rights(user_id)))),
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_rights")]
    )

    await bot.edit_message_text(
        "Какое право ему добавим?",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith("add_right"), state=BotStates.USER_RIGHTS)
async def add_right_arg_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    right = callback.data.split("&")[1]

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.add_right(user_id, right)

    user_rights = Users.get_user_rights(user_id)

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda r: types.KeyboardButton(r, callback_data=f"add_right&{r}"),
                sorted(set(Rights.comments.keys()) - set(map(lambda r: r.name, Users.get_user_rights(user_id)))),
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_rights")]
    )

    await bot.edit_message_text(
        (", ".join(list(map(lambda r: r.name, user_rights))) or "Нет прав") + f"\nПраво {right} добавлено",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data == "del_right", state=BotStates.USER_RIGHTS)
async def del_right_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda r: types.KeyboardButton(r.name, callback_data=f"del_right&{r.name}"),
                sorted(Users.get_user_rights(user_id), key=lambda r: r.name)
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_rights")]
    )

    await bot.edit_message_text(
        "Какое право у него заберем?",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith("del_right"), state=BotStates.USER_RIGHTS)
async def del_right_arg_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    right = callback.data.split("&")[1]

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.del_right(user_id, right)

    user_rights = Users.get_user_rights(user_id)

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *list(
            map(
                lambda r: types.KeyboardButton(r.name, callback_data=f"del_right&{r.name}"),
                sorted(user_rights, key=lambda r: r.name)
            )
        )
        + [types.KeyboardButton("🔙 Назад", callback_data="user_rights")]
    )

    await bot.edit_message_text(
        (", ".join(list(map(lambda r: r.name, user_rights))) or "Нет прав") + f"\nПраво {right} удалено",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data == "user_data", state=BotStates.USER_RIGHTS)
async def user_data_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("USERNAME", callback_data="edit_username"),
            types.KeyboardButton("ИМЯ", callback_data="edit_name"),
            types.KeyboardButton("ФАМИЛИЯ", callback_data="edit_surname"),
            types.KeyboardButton("ДОЛЖНОСТЬ", callback_data="edit_post"),
            types.KeyboardButton("🔙 Назад", callback_data=f"user_menu&{user_id}"),
        ]
    )

    await bot.edit_message_text(
        f"{Users.get_readable_info(user_id)}\nКакую информацию будем менять?",
        callback.message.chat.id,
        callback.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data == "edit_username", state=BotStates.USER_RIGHTS)
async def edit_id_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    await BotStates.WAIT_FOR_USERNAME.set()

    async with state.proxy() as data:
        data["chosen_user"] = user_id

    await bot.edit_message_text(
        "Введите новый username (без @ в начале)",
        callback.message.chat.id,
        callback.message.message_id,
    )


@dp.message_handler(state=BotStates.WAIT_FOR_USERNAME)
async def username_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.update_user(user_id, username=msg.text)

    await dp.current_state(user=msg.from_user.id).reset_state()
    await BotStates.USER_RIGHTS.set()
    async with state.proxy() as data:
        data["chosen_user"] = user_id

    async with state.proxy() as data:
        data["chosen_user"] = user_id

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("USERNAME", callback_data="edit_username"),
            types.KeyboardButton("ИМЯ", callback_data="edit_name"),
            types.KeyboardButton("ФАМИЛИЯ", callback_data="edit_surname"),
            types.KeyboardButton("ДОЛЖНОСТЬ", callback_data="edit_post"),
            types.KeyboardButton("🔙 Назад", callback_data=f"user_menu&{user_id}"),
        ]
    )

    await msg.answer(
        f"{Users.get_readable_info(user_id)}\nКакую информацию будем менять?",
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data == "edit_name", state=BotStates.USER_RIGHTS)
async def edit_name_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    await BotStates.WAIT_FOR_NAME.set()

    async with state.proxy() as data:
        data["chosen_user"] = user_id

    await bot.edit_message_text(
        "Введите новое имя", callback.message.chat.id, callback.message.message_id
    )


@dp.callback_query_handler(lambda callback: callback.data == "edit_surname", state=BotStates.USER_RIGHTS)
async def edit_surname_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    await BotStates.WAIT_FOR_SURNAME.set()

    async with state.proxy() as data:
        data["chosen_user"] = user_id

    await bot.edit_message_text(
        "Введите новую фамилию", callback.message.chat.id, callback.message.message_id
    )


@dp.message_handler(state=BotStates.WAIT_FOR_NAME)
async def name_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.update_user(user_id, name=msg.text)

    await dp.current_state(user=msg.from_user.id).reset_state()

    await BotStates.USER_RIGHTS.set()

    async with state.proxy() as data:
        data["chosen_user"] = user_id

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("USERNAME", callback_data="edit_username"),
            types.KeyboardButton("ИМЯ", callback_data="edit_name"),
            types.KeyboardButton("ФАМИЛИЯ", callback_data="edit_surname"),
            types.KeyboardButton("ДОЛЖНОСТЬ", callback_data="edit_post"),
            types.KeyboardButton("🔙 Назад", callback_data=f"user_menu&{user_id}"),
        ]
    )

    await msg.answer(
        f"{Users.get_readable_info(user_id)}\nКакую информацию будем менять?",
        reply_markup=kb,
    )


@dp.message_handler(state=BotStates.WAIT_FOR_SURNAME)
async def surname_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.update_user(user_id, surname=msg.text)

    await dp.current_state(user=msg.from_user.id).reset_state()

    await BotStates.USER_RIGHTS.set()

    async with state.proxy() as data:
        data["chosen_user"] = user_id

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("USERNAME", callback_data="edit_username"),
            types.KeyboardButton("ИМЯ", callback_data="edit_name"),
            types.KeyboardButton("ФАМИЛИЯ", callback_data="edit_surname"),
            types.KeyboardButton("ДОЛЖНОСТЬ", callback_data="edit_post"),
            types.KeyboardButton("🔙 Назад", callback_data=f"user_menu&{user_id}"),
        ]
    )

    await msg.answer(
        f"{Users.get_readable_info(user_id)}\nКакую информацию будем менять?",
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda callback: callback.data == "edit_post", state=BotStates.USER_RIGHTS)
async def edit_post_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    async with state.proxy() as data:
        user_id = data["chosen_user"]

    await BotStates.WAIT_FOR_POST.set()

    async with state.proxy() as data:
        data["chosen_user"] = user_id

    await bot.edit_message_text(
        "Введите новую должность", callback.message.chat.id, callback.message.message_id
    )


@dp.message_handler(state=BotStates.WAIT_FOR_POST)
async def post_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data["chosen_user"]

    Users.update_user(user_id, post=msg.text)

    await dp.current_state(user=msg.from_user.id).reset_state()

    await BotStates.USER_RIGHTS.set()

    async with state.proxy() as data:
        data["chosen_user"] = user_id

    kb = types.InlineKeyboardMarkup(row_width=1).add(
        *[
            types.KeyboardButton("USERNAME", callback_data="edit_username"),
            types.KeyboardButton("ИМЯ", callback_data="edit_name"),
            types.KeyboardButton("ФАМИЛИЯ", callback_data="edit_surname"),
            types.KeyboardButton("ДОЛЖНОСТЬ", callback_data="edit_post"),
            types.KeyboardButton("🔙 Назад", callback_data=f"user_menu&{user_id}"),
        ]
    )

    await msg.answer(
        f"{Users.get_readable_info(user_id)}\nКакую информацию будем менять?",
        reply_markup=kb,
    )

####

# TODO: пролистываение пунктов меню
