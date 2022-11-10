from aiogram.utils import markdown

from database.base import db_session
from database.database import Database
from database.models import User, City, Right, user_right, user_managers, user_city
from specials.singleton import Singleton


class Rights:
    """
    A class to represent a user's rights.

    GET_MAP право на получение карты по её номеру
    GET_ADDRESS право на получение карт по адресу
        если отработает и надо получить карту, то требуются права уровня GET_MAP
    CITY_MANAGEMENT право на управление городами
        позволяет удалять, создавать, назначать админов и их права для того или иного города
    CHANGE_USER_PERMISSIONS изменение прав других пользователей
    """

    GET_MAP = "GET_MAP"
    GET_ADDRESS = "GET_ADDRESS"
    CITY_MANAGEMENT = "CITY_MANAGEMENT"
    CHANGE_USER_PERMISSIONS = "CHANGE_USER_PERMISSIONS"

    # TODO переработать систему прав

    comments = {
        "GET_MAP": "🗺️ Карта",
        "GET_ADDRESS": "🗺️ Адрес",
        "CITY_MANAGEMENT": "🏢 Изменение городов",
        "CHANGE_USER_PERMISSIONS": "🔐 Права пользователей",
    }


class Users(metaclass=Singleton):
    @classmethod
    def toggle_super(cls, tg_id):
        with db_session(mode="w") as session:
            user = session.query(User).filter(User.tg_id == str(tg_id)).first()
            user.superuser = not user.superuser

    @classmethod
    def get_users(cls) -> list[User]:
        with db_session() as session:
            return session.query(User).all()

    @classmethod
    def get_user(cls, tg_id=None, user_id=None) -> User:
        """
        Returns a user object from database

        :param tg_id: Telegram id of the user
        :type tg_id: str
        :param user_id: ID of the user in database
        :type user_id: int
        """
        if tg_id and user_id:
            print("DONT'T USE tg_id and user_id TOGETHER")
            raise Exception
        if not tg_id and not user_id:
            print("EMPTY SEARCH")
            raise Exception
        with db_session() as session:
            if tg_id:
                return session.query(User).filter(User.tg_id == str(tg_id)).first()
            return session.query(User).filter(User.id == user_id).first()

    @classmethod
    def get_user_rights(cls, tg_id):
        with db_session() as session:
            return (
                session.query(Right)
                .join(user_right, Right.id == user_right.right_id)
                .join(User, User.id == user_right.user_id)
                .filter(User.tg_id == str(tg_id)).all()
            )

    @classmethod
    def new_user(cls, tg_id, username=None, post=None, name=None, surname=None):
        with db_session(mode='w') as session:
            session.add(User(tg_id, username, post, name, surname))

    @classmethod
    def del_user(cls, user_id=None, tg_id=None):
        if not user_id and not tg_id:
            print("Хоть что-то выбери")
            raise Exception
        if user_id and tg_id:
            print("Нельзя использовать и то и то")
            raise Exception

        with db_session(mode='w') as session:
            if user_id:
                session.query(User).filter(User.id == user_id).delete()
            if tg_id:
                session.query(User).filter(User.tg_id == tg_id).delete()

    @classmethod
    def update_user(cls, tg_id, username=None, post=None, name=None, surname=None):
        with db_session(mode="w") as session:
            user = session.query(User).filter(User.tg_id == str(tg_id)).first()
            user.username = username or user.username
            user.post = post or user.post
            user.name = name or user.name
            user.surname = surname or user.surname

    @classmethod
    def get_cities(cls, tg_id) -> list[City]:
        with db_session() as session:
            return (
                session.query(City)
                .join(user_city, user_city.city_id == City.id)
                .join(User, user_city.user_id == User.id)
                .filter(User.tg_id == str(tg_id))
                .all()
            )

    @classmethod
    def add_city(cls, tg_id, city_name):
        with db_session(mode="w") as session:
            user = session.query(User).filter(User.tg_id == str(tg_id)).first()
            city = session.query(City).filter(City.name.ilike(city_name)).first()
            session.add(user_city(user.id, city.id))

    @classmethod
    def del_city(cls, tg_id, city_name):
        with db_session(mode="w") as session:
            user = session.query(User).filter(User.tg_id == str(tg_id)).first()
            city = session.query(City).filter(City.name.ilike(city_name)).first()
            session.query(user_city).filter(user_city.user_id == user.id).filter(user_city.city_id == city.id).delete()

    @classmethod
    def add_right(cls, tg_id, right_name):
        with db_session(mode="w") as session:
            user = cls.get_user(tg_id)
            right = session.query(Right).filter(Right.name.ilike(right_name)).first()
            session.add(user_right(user.id, right.id))

    @classmethod
    def del_right(cls, tg_id, right_name):
        with db_session(mode="w") as session:
            user = cls.get_user(tg_id)
            right = session.query(Right).filter(Right.name.ilike(right_name)).first()
            session.query(user_right).filter(user_right.user_id == user.id).filter(
                user_right.right_id == right.id).delete()

    @classmethod
    def add_manager(cls, slave_tg_id, master_tg_id):
        with db_session(mode="w") as session:
            slave = session.query(User).filter(User.tg_id == str(slave_tg_id)).first()
            master = session.query(User).filter(User.tg_id == str(master_tg_id)).first()
            session.add(user_managers(slave.id, master.id))

    @classmethod
    def del_manager(cls, user_tg_id, master_tg_id):
        with db_session(mode="w") as session:
            slave = session.query(User).filter(User.tg_id == str(user_tg_id)).first()
            master = session.query(User).filter(User.tg_id == str(master_tg_id)).first()
            session.query(user_managers).filter(user_managers.user_id == slave.id).filter(
                user_managers.manager_id == master.id).delete()

    @classmethod
    def get_slaves(cls, tg_id) -> list[User]:
        with db_session() as session:
            # return cls.get_users()

            user = session.query(User).filter(User.tg_id == str(tg_id)).first()
            slaves_ids = session.query(user_managers).filter(user_managers.manager_id == user.id).all()
            if user.superuser:
                return session.query(User).filter(
                    User.id.in_(list(map(lambda slave: slave.user_id, slaves_ids)))).all() + [user]
            return session.query(User).filter(User.id.in_(list(map(lambda slave: slave.user_id, slaves_ids)))).all()

    @classmethod
    def get_masters(cls, tg_id) -> list[User]:
        with db_session() as session:
            # return cls.get_users()

            user = session.query(User).filter(User.tg_id == str(tg_id)).first()
            masters_ids = session.query(user_managers).filter(user_managers.user_id == user.id).all()
            return session.query(User).filter(
                User.id.in_(list(map(lambda master: master.manager_id, masters_ids)))).all()

    @classmethod
    def get_readable_info(cls, tg_id) -> str:
        user = cls.get_user(tg_id)

        res = f"id{user.tg_id}"
        if user.username:
            res += f"\n@{user.username}"
        if user.name:
            res += f"\n{markdown.hbold('Имя:')} {user.name}"
        if user.surname:
            res += f"\n{markdown.hbold('Фамилия:')} {user.surname}"
        if user.post:
            res += f"\n{markdown.hbold('Должность:')} {user.post}"
        if user_cities := cls.get_cities(user.tg_id):
            if len(user_cities) == len(Database.get_cities()):
                res += f"\n{markdown.hbold('Город:')} любой"
            else:
                res += f"\n{markdown.hbold('Города:')} " + ", ".join(list(map(lambda city: city.name, user_cities)))
        if user_rights := cls.get_user_rights(tg_id):
            if len(user_rights) == len(list(Rights.comments.keys())):
                res += f"\n{markdown.hbold('Права:')} все"
            else:
                res += f"\n{markdown.hbold('Права:')} " + ", ".join(list(map(lambda right: right.name, user_rights)))
        return res

    @classmethod
    def get_readable_name(cls, user_obj: User = None, ) -> str:
        return (
                   f"{user_obj.name} {user_obj.surname}"
                   if user_obj.name and user_obj.surname
                   else None
               ) or user_obj.username or user_obj.tg_id

    @classmethod
    def get_user_actions(cls, tg_id) -> list[str]:
        user_rights = cls.get_user_rights(tg_id)
        return list(map(lambda r: Rights.comments.get(r.name), user_rights))
