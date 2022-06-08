# import logging


# class CustomFilter(logging.Filter):

#     COLOR = {
#         "DEBUG": "GREEN",
#         "INFO": "GREEN",
#         "WARNING": "YELLOW",
#         "ERROR": "RED",
#         "CRITICAL": "RED",
#     }

#     def filter(self, record):
#         record.color = CustomFilter.COLOR[record.levelname]
#         return True


# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - [%(levelname)s] - [%(color)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
# )

# logger = logging.getLogger(__name__)
# logger.addFilter(CustomFilter())

# logger.debug("сообщение для отладки, цвет — зеленый")
# logger.info("информационное сообщение, цвет — зеленый")
# logger.warning("предупреждающее сообщение, цвет — желтый")
# logger.error("сообщение об ошибке, цвет — красный")
# logger.critical("сообщение о критической ошибке, цвет — красный")

