from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String, Boolean
from sqlalchemy.orm import relationship

from database.base import Base


class City(Base):
    """
    Represents a city in the database.
    """

    __tablename__ = "city"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    regions = relationship(
        "Region",
        backref="city",
        passive_deletes="all",
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return f"<City: '{self.name}'>"


class Region(Base):
    """
    Represents a region in the database.
    """

    __tablename__ = "region"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city_id = Column(
        Integer,
        ForeignKey("city.id", ondelete="CASCADE"),
        nullable=False,
    )
    maps = relationship(
        "Map",
        backref="region",
        passive_deletes="all",
    )

    def __init__(self, name, city_id):
        self.name = name
        self.city_id = city_id

    def __repr__(self) -> str:
        return f"<Region: '{self.name}', '{self.city_id}'>"


class Map(Base):
    """
    Represents a map in the database.
    """

    __tablename__ = "map"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    picture = Column(LargeBinary)
    region_id = Column(
        Integer,
        ForeignKey("region.id", ondelete="CASCADE"),
        nullable=False,
    )
    addresses = relationship(
        "Address",
        backref="map",
        passive_deletes="all",
    )

    def __init__(self, name, picture_bytes, region_id):
        self.name = name
        self.picture = picture_bytes
        self.region_id = region_id

    def __repr__(self) -> str:
        return f"<Map: '{self.name}', '{self.region_id}'>"


class Address(Base):
    """
    Represents an address in the database.
    """

    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    street = Column(String)
    number = Column(String)
    floors = Column(Integer, nullable=True)
    entrances = Column(Integer, nullable=True)
    flats = Column(Integer)  # квартиры
    mailboxes = Column(Integer, nullable=True)
    comment = Column(String, nullable=True)
    map_id = Column(
        Integer,
        ForeignKey("map.id", ondelete="CASCADE"),
        nullable=False,
    )

    def __init__(
            self,
            street,
            number,
            floors,
            entrances,
            flats,
            mailboxes,
            comment,
            map_id
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
        return f"<Address: '{self.street}', '{self.number}', '{self.floors}', " \
               f"'{self.entrances}', '{self.flats}', '{self.mailboxes}', '{self.comment}', '{self.map_id}'>"


class user_city(Base):
    __tablename__ = "user_city"
    user_id = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    city_id = Column(ForeignKey("city.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    city = relationship("City")

    def __init__(self, user_id, city_id):
        self.user_id = user_id
        self.city_id = city_id

    def __repr__(self) -> str:
        return f"<user_city: '{self.user_id}', '{self.city_id}'>"


class user_right(Base):
    __tablename__ = "user_right"
    user_id = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    right_id = Column(ForeignKey("right.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    right = relationship("Right")

    def __init__(self, user_id, right_id):
        self.user_id = user_id
        self.right_id = right_id

    def __repr__(self):
        return f"<user_managers: '{self.user_id}', '{self.right_id}'>"


class user_managers(Base):
    __tablename__ = "user_managers"
    user_id = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    manager_id = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    manager = relationship("User", foreign_keys=[manager_id])

    def __init__(self, user_id, manager_id):
        self.user_id = user_id
        self.manager_id = manager_id

    def __repr__(self):
        return f"<user_managers: '{self.user_id}', '{self.manager_id}'>"


class User(Base):
    """
    Represents a user in the database.
    """

    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    tg_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)
    post = Column(String, nullable=True)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    superuser = Column(Boolean, default=False)
    cities = relationship("user_city")
    rights = relationship("user_right")
    managers = relationship("user_managers", foreign_keys="user_managers.manager_id")

    def __init__(self, tg_id, username=None, post=None, name=None, surname=None):
        self.tg_id = tg_id
        self.username = username
        self.post = post
        self.name = name
        self.surname = surname

    def __repr__(self) -> str:
        return f"<User: '{self.tg_id}', '{self.username}', '{self.post}', '{self.name}', '{self.surname}', '{self.superuser}'>"


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
