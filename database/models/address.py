from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
