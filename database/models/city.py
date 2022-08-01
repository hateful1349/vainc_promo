from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database.models.region import Region

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
