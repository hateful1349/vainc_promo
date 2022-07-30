from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class City(Base):
    __tablename__ = "city"
    city_id = Column(Integer, primary_key=True)
    name = Column(String)
    regions = relationship("Region", backref="city")

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return f"<City: '{self.name}', '{self.regions}'>"


class Region(Base):
    __tablename__ = "region"
    region_id = Column(Integer, primary_key=True)
    name = Column(String)
    city_id = Column(Integer, ForeignKey("city.city_id"))
    maps = relationship("Map", backref="region")

    def __init__(self, name, city_id):
        self.name = name
        self.city_id = city_id

    def __repr__(self) -> str:
        return f"<Region: '{self.name}', '{self.city_id}', '{self.maps}'>"


class Map(Base):
    __tablename__ = "map"
    map_id = Column(Integer, primary_key=True)
    name = Column(String)
    picture = Column(LargeBinary)
    region_id = Column(Integer, ForeignKey("region.region_id"))
    addresses = relationship("Address", backref="map")

    def __init__(self, name, picture_bytes, region_id):
        self.name = name
        self.picture = picture_bytes
        self.region_id = region_id

    def __repr__(self) -> str:
        return (
            f"<Map: '{self.name}', 'picture', '{self.region_id}', '{self.addresses}'>"
        )


class Address(Base):
    __tablename__ = "address"
    address_id = Column(Integer, primary_key=True)
    street = Column(String)
    number = Column(String)
    floors = Column(Integer, nullable=True)
    entrances = Column(Integer, nullable=True)
    flats = Column(Integer)  # квартиры
    mailboxes = Column(Integer, nullable=True)
    comment = Column(String, nullable=True)
    map_id = Column(Integer, ForeignKey("map.map_id"))

    def __init__(
        self,
        street,
        number,
        floors,
        entrances,
        flats,
        map_id,
        mailboxes=None,
        comment=None,
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
        return f"<Address: '{self.street}', '{self.number}', '{self.floors}', '{self.entrances}', '{self.flats}', '{self.mailboxes}', '{self.comment}', '{self.map_id}'>"
