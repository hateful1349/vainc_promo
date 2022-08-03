from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    DEFAULT = State()
    MAP = State()
    ADDRESS = State()

    NEW_PROM_FNAME = State()
    NEW_PROM_LNAME = State()
    NEW_PROM_ADDRESS = State()
    NEW_PROM_PHONE_NUMBER = State()
    NEW_PROM_PHONE_PAYMENTS = State()

    CITY = State()

    CITY_FOR_MAPS = State()
    WAIT_FOR_CITY_RESOURCES = State()
