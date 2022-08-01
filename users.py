import json
import os
from typing import Dict

from data import config
from database.database import Database as db
from specials.singleton import Singleton


class Rights:
    GET_MAP = "GET_MAP"
    GET_ADDRESS = "GET_ADDRESS"
    CITY_MANAGEMENT = "CITY_MANAGEMENT"
    CHANGE_USER_PERMISSIONS = "CHANGE_USER_PERMISSIONS"

    comments = {
        "GET_MAP": "🗺️ Карта",
        "GET_ADDRESS": "🗺️ Адрес",
        "CITY_MANAGEMENT": "🏢 Изменение городов",
        "CHANGE_USER_PERMISSIONS": "🔐 Права пользователей",
    }


class Users(metaclass=Singleton):
    @classmethod
    def get_users(cls) -> dict:
        with open(
            os.path.join(
                os.path.dirname(__file__),
                config.USERS_DB_FILE,
            )
        ) as f:
            users: Dict[str : Dict[str, str | None]] = json.load(f)
        return users

    @classmethod
    def get_main_admins(cls):
        users = cls.get_users()
        return list(
            map(
                lambda user_id: f"@{users.get(user_id).get('username')}"
                if users.get(user_id).get("username") not in [None, ""]
                else f"id{user_id}",
                list(users.keys())[:3],
            )
        )

    @classmethod
    def get_user(cls, user_id):
        user_id = str(user_id)
        return cls.get_users().get(user_id)

    @classmethod
    def get_user_rights(cls, user_id) -> set:
        user = cls.get_user(user_id)
        if user is None:
            return set()
        if user.get("rights") is None or user.get("rights") == []:
            return set()
        return set(user.get("rights"))

    @classmethod
    def get_user_actions(cls, user_id):
        user_rights = cls.get_user_rights(user_id)
        return list(map(lambda r: Rights.comments.get(r), user_rights))

    @classmethod
    def get_user_cities(cls, user_id):
        user = cls.get_user(user_id)
        if user is None:
            return None
        cities = user.get("city")
        if cities is None or not list(filter(lambda city: city != "", cities)):
            return None
        if cities == "ANY":
            cities = list(map(lambda city: city.name, db.get_cities()))
        return cities

    @classmethod
    def get_management(cls, user_id):
        user = cls.get_user(user_id)
        if user.get("managers") is None:
            return None
        managers = set(user.get("managers"))
        for manager in user.get("managers"):
            managers |= cls.get_management(manager) or set()
        return managers

    @classmethod
    def get_information(cls, user_id):
        res = f"id{user_id}"
        if cls.get_user(user_id).get("username"):
            res += f"\n@{cls.get_user(user_id).get('username')}"
        if cls.get_user(user_id).get("name"):
            res += f"\nИмя: {cls.get_user(user_id).get('name')}"
        if cls.get_user(user_id).get("post"):
            res += f"\nДолжность: {cls.get_user(user_id).get('post')}"
        if cls.get_user_cities(user_id):
            if cls.get_user_cities(user_id) == list(
                map(lambda city: city.name, db.get_cities())
            ):
                res += "\nГород: любой"
            else:
                res += f"\nГорода: {' '.join(cls.get_user_cities(user_id))}"
        if len(cls.get_user_rights(user_id)) > 0:
            res += "\nПрава: " + "\n\t".join(cls.get_user_rights(user_id))
        if cls.get_management(user_id):
            managers_ids = list(cls.get_management(user_id))
            managers = list(
                map(
                    lambda user: cls.get_user(user_id).get("username")
                    or cls.get_user(user_id).get("name")
                    or user,
                    managers_ids,
                )
            )
            res += f"\nРуководство: {' '.join(managers)}"
        return res


# легенда
# GET_MAP право на получение карты по её номеру
#     требует права доступа CITY
# GET_ADDRESS право на получение карт по адресу
#     требует права доступа CITY
#     если отработает и надо получить карту, то требуются права уровня GET_MAP
# CITY_MANAGEMENT право на управление городами
#     позволяет удалять, создавать, назначать админов и их права для того или иного города
# CHANGE_USER_PERMISSIONS изменение прав других пользователей
