from aiogram.utils.helper import Helper, HelperMode, ListItem


class BotStates(Helper):
    mode = HelperMode.snake_case

    DEFAULT = ListItem()
    MAP = ListItem()
    ADDRESS = ListItem()

    NEW_PROM_FNAME = ListItem()
    NEW_PROM_LNAME = ListItem()
    NEW_PROM_ADDRESS = ListItem()
    NEW_PROM_PHONE_NUMBER = ListItem()
    NEW_PROM_PHONE_PAYMENTS = ListItem()
