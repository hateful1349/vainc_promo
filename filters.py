import json
import os
from typing import List, Union

from aiogram.dispatcher.filters.filters import BoundFilter
from aiogram.types import Message

from base import dp
from helpers import read_config
from users import admins_id


class AdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin: str):
        self.is_admin = is_admin

    async def check(self, message: Message):
        return str(message.from_user.id) in admins_id


class ImprovedUserFilter(BoundFilter):
    key = "user_have_rights"

    def __init__(self, user_have_rights: Union[str, List[str]]):
        if isinstance(user_have_rights, str):
            user_have_rights = user_have_rights.split()
        self.user_have_rights = user_have_rights

    async def check(self, msg: Message):
        config = read_config()
        with open(
            os.path.dirname(__file__)
            + "/configs"
            + dict(config).get("USERS").get("users_file")
        ) as f:
            users = json.load(f)

        return set(self.user_have_rights) <= set(
            users[str(msg.from_user.id)]["rights"].split()
        )


def bind_filters():
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(ImprovedUserFilter)
