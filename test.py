# import yadisk
# from helpers import read_config

# import openpyxl

# config = read_config()
# token = config['YANDEX_API']['oauth_token']

# y = yadisk.YaDisk(token=token)
# # или
# # y = yadisk.YaDisk("<id-приложения>", "<secret-приложения>", "<токен>")

# # Проверяет, валиден ли токен
# print(y.check_token())

# # Получает общую информацию о диске
# # print(y.get_disk_info())

# # # Выводит содержимое "/some/path"
# # print(list(y.listdir("/some/path")))

# # # Загружает "file_to_upload.txt" в "/destination.txt"
# # y.upload("file_to_upload.txt", "/destination.txt")

# # # То же самое
# # with open("file_to_upload.txt", "rb") as f:
# #     y.upload(f, "/destination.txt")

# # Скачивает "/some-file-to-download.txt" в "downloaded.txt"
# # y.download("/Новая таблица.xlsx", "table.xlsx")

# # # Безвозвратно удаляет "/file-to-remove"
# # y.remove("/file-to-remove", permanently=True)

# # # Создаёт новую папку "/test-dir"
# # print(y.mkdir("/test-dir1"))


# wookbook = openpyxl.load_workbook("table.xlsx")
# # Define variable to read the active sheet:
# worksheet = wookbook.active
# # Iterate the loop to read the cell values
# for i in range(0, worksheet.max_row):
#     for col in worksheet.iter_cols(1, worksheet.max_column):
#         print(col[i].value, end="\t\t")
#     print('')


# from helpers import read_config

# config = read_config()
# print(dict(config).get("USERS").get("admins"))

# print(dict(config).get("USERS").get("devs"))
# print(config["USERS"]["region_admins"].split("\n"))

# import json
# import os

# with open(os.path.dirname(__file__) + "/configs/users.json") as f:
#     users = dict(json.load(f))

# for user, values in users.items():
#     print(user, values)

# from users import Rights

# print(getattr(Rights, "GET_MAP"))
# getattr
