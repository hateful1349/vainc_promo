from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    WAIT_FOR_MAP = State()
    WAIT_FOR_ADDRESS = State()

    WAIT_FOR_MAP_CITY = State()
    WAIT_FOR_ADDRESS_CITY = State()

    WAIT_FOR_USER_ID = State()
    WAIT_FOR_USERNAME = State()
    WAIT_FOR_NAME = State()
    WAIT_FOR_SURNAME = State()
    WAIT_FOR_POST = State()

    WAIT_FOR_CITY_NAME = State()
    WAIT_FOR_CITY_XLSX = State()
    WAIT_FOR_CITY_ZIP = State()
    WAIT_FOR_CITY_BIG_ZIP = State()
