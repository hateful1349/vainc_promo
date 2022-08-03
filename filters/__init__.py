from loader import dp

from filters.filters import UserStatusFilter

if __name__ == "filters":
    dp.filters_factory.bind(UserStatusFilter)
