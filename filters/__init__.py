from filters.filters import UserStatusFilter
from loader import dp

if __name__ == "filters":
    dp.filters_factory.bind(UserStatusFilter)
