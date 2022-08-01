from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database.models.map import Map

Base = declarative_base()


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
