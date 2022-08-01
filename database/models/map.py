from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database.models.address import Address

Base = declarative_base()


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
