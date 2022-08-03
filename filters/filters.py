from typing import List, Union

from aiogram.dispatcher.filters.filters import BoundFilter
from aiogram.types import Message
from utils.users import Users


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
        return set(self.user_have_rights) <= Users.get_user_rights(msg.from_user.id)
