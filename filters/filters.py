from typing import List, Union

from aiogram.dispatcher.filters.filters import BoundFilter
from aiogram.types import Message

from database.users import Users


class UserStatusFilter(BoundFilter):
    """
    Filter users by their status.
    """

    key = "user_have_rights"

    def __init__(self, user_have_rights: Union[str, List[str]]):
        if isinstance(user_have_rights, str):
            user_have_rights = user_have_rights.split()
        self.user_have_rights = user_have_rights

    async def check(self, msg: Message):
        req_rights = set(self.user_have_rights)
        user_rights = set(
            map(
                lambda r: r.name,
                Users.get_user_rights(msg.from_user.id)
            )
        )
        return req_rights <= user_rights
