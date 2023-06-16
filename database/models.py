from typing import List, Optional
from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String, Boolean, false
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.base import Base


class City(Base):
    __tablename__ = "city"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    regions: Mapped[List["Region"]] = relationship(passive_deletes="all")

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return f"<City: '{self.name}'>"


class Region(Base):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    city_id = mapped_column(
        ForeignKey(
            "city.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    maps: Mapped[List["Map"]] = relationship(passive_deletes="all")

    def __init__(self, name, city_id):
        self.name = name
        self.city_id = city_id

    def __repr__(self) -> str:
        return f"<Region: '{self.name}', '{self.city_id}'>"


class Map(Base):
    __tablename__ = "map"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    picture: Mapped[bytes]
    region_id = mapped_column(
        ForeignKey(
            "region.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    addresses: Mapped[List["Address"]] = relationship(passive_deletes="all")

    def __init__(self, name, picture_bytes, region_id):
        self.name = name
        self.picture = picture_bytes
        self.region_id = region_id

    def __repr__(self) -> str:
        return f"<Map: '{self.name}', '{self.region_id}'>"


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str]
    number: Mapped[str]
    floors: Mapped[int] = mapped_column(nullable=True)
    entrances: Mapped[int] = mapped_column(nullable=True)
    flats: Mapped[int]  # квартиры
    mailboxes: Mapped[int] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
    map_id = mapped_column(
        ForeignKey(
            "map.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    def __init__(
        self, street, number, floors, entrances, flats, mailboxes, comment, map_id
    ):
        self.street = street
        self.number = number
        self.floors = floors
        self.entrances = entrances
        self.flats = flats
        self.mailboxes = mailboxes
        self.comment = comment
        self.map_id = map_id

    def __repr__(self) -> str:
        return (
            f"<Address: '{self.street}', '{self.number}', '{self.floors}', "
            f"'{self.entrances}', '{self.flats}', '{self.mailboxes}', '{self.comment}', '{self.map_id}'>"
        )


class user_city(Base):
    __tablename__ = "user_city"

    user_id = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    city_id = mapped_column(
        ForeignKey("city.id", ondelete="CASCADE"),
        nullable=False,
    )
    city = relationship("City")

    def __init__(self, user_id, city_id):
        self.user_id = user_id
        self.city_id = city_id

    def __repr__(self) -> str:
        return f"<user_city: '{self.user_id}', '{self.city_id}'>"


class user_right(Base):
    __tablename__ = "user_right"

    user_id = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    right_id = mapped_column(
        ForeignKey("right.id", ondelete="CASCADE"),
        nullable=False,
    )
    right = relationship("Right")

    def __init__(self, user_id, right_id):
        self.user_id = user_id
        self.right_id = right_id

    def __repr__(self):
        return f"<user_managers: '{self.user_id}', '{self.right_id}'>"


class user_managers(Base):
    __tablename__ = "user_managers"

    user_id = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    manager_id = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    manager = relationship("User", foreign_keys=[manager_id])

    def __init__(self, user_id, manager_id):
        self.user_id = user_id
        self.manager_id = manager_id

    def __repr__(self):
        return f"<user_managers: '{self.user_id}', '{self.manager_id}'>"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(nullable=True)
    post: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    surname: Mapped[str] = mapped_column(nullable=True)
    superuser: Mapped[bool] = mapped_column(default=False)
    cities = relationship("user_city")
    rights = relationship("user_right")
    managers = relationship("user_managers", foreign_keys="user_managers.manager_id")

    def __init__(
        self,
        tg_id: int,
        username: Optional[str],
        post: Optional[str],
        name: Optional[str],
        surname: Optional[str],
    ):
        self.tg_id = tg_id
        self.username = username
        self.post = post
        self.name = name
        self.surname = surname

    def __repr__(self) -> str:
        return (
            f"<User: '{self.tg_id}', "
            f"'{self.username}', "
            f"'{self.post}', "
            f"'{self.name}', "
            f"'{self.surname}', "
            f"'{self.superuser}'>"
        )


class Right(Base):
    """
    Represents a right in the database
    """

    __tablename__ = "right"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return f"<Right: '{self.name}'>"
