from aiogram.types import Message

from base import bot, dp
from helpers import (
    get_address,
    get_fname,
    get_lname,
    get_phone,
    set_address,
    set_chat_id,
    set_fname,
    set_lname,
    set_phone,
)
from states import BotStates


@dp.message_handler(commands=["new_prom"])
async def add_new_prom(msg: Message):
    await bot.send_message(msg.chat.id, "Добро пожаловать в нашу команду!")
    await bot.send_message(msg.chat.id, "Представьтесь, пожалуйста")
    await bot.send_message(msg.chat.id, "Как вас зовут?")
    await dp.current_state(chat=msg.chat.id).set_state(BotStates.all()[3])


@dp.message_handler(state=BotStates.all()[3])
async def get_prom_fname(msg: Message):
    set_fname(msg.from_user.id, msg.text)
    await bot.send_message(
        msg.chat.id, f"Отлично! Буду к вам обращаться {msg.text.capitalize()}"
    )
    await bot.send_message(msg.chat.id, "Теперь, пожалуйста, напишите вашу фамилию")
    await dp.current_state(chat=msg.chat.id).set_state(BotStates.all()[4])


@dp.message_handler(state=BotStates.all()[4])
async def get_prom_lname(msg: Message):
    set_lname(msg.from_user.id, msg.text)
    await bot.send_message(
        msg.chat.id,
        f"Приятно познакомиться, {get_lname(msg.from_user.id).capitalize()} {get_fname(msg.from_user.id).capitalize()}",
    )
    await bot.send_message(
        msg.chat.id, "Укажите, по какому номеру телефона с вами можно связаться?"
    )
    await dp.current_state(chat=msg.chat.id).set_state(BotStates.all()[5])


@dp.message_handler(state=BotStates.all()[5])
async def get_prom_phone(msg: Message):
    set_phone(msg.from_user.id, msg.text)
    await bot.send_message(
        msg.chat.id,
        f"Хорошо, при крайней необходимости будем звонить по номеру {get_phone(msg.from_user.id)}",
    )
    await bot.send_message(
        msg.chat.id,
        'Теперь, пожалуйста, подскажите, где вы живете, чтобы мы знали, в каком районе находится ваша "домашняя" карта',
    )
    await dp.current_state(chat=msg.chat.id).set_state(BotStates.all()[6])


@dp.message_handler(state=BotStates.all()[6])
async def get_prom_address(msg: Message):
    set_address(msg.from_user.id, msg.text)
    set_chat_id(msg.from_user.id, msg.chat.id)
    await bot.send_message(msg.chat.id, f"Спасибо")
    await bot.send_message(
        msg.chat.id,
        f"{get_lname(msg.from_user.id).capitalize()} {get_fname(msg.from_user.id).capitalize()}\n{get_address(msg.from_user.id)}\n{get_phone(msg.from_user.id)}\n",
    )
    await bot.send_message(
        msg.chat.id,
        "Всё верно?\n(ответ не обязателен, тк автор бота пока что не допилил)",
    )
    # dp.current_state(chat=msg.chat.id).set_state(BotStates.all()[5])
    await dp.current_state(chat=msg.chat.id).reset_state()
