import datetime
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Tuple, Union
from zipfile import ZipFile

from data import config
from openpyxl import load_workbook
from specials.singleton import Singleton
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Address, City, Map, Region


@contextmanager
def db_session(engine, mode="r"):
    """
    Generates a session for the given engine
    :param engine: the engine to use
    :param mode: the mode to use ('w' to commit the query on the exit, 'r' to only read from database)
    """
    session = sessionmaker(bind=engine)()
    try:
        yield session
        if mode == "w":
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class Database(metaclass=Singleton):
    _engine = None

    @classmethod
    def init_engine(cls, engine=None, echo=False) -> bool:
        """
        Initializes the database engine
        """
        if cls._engine is None:
            if engine is None or engine in ["sql"]:
                cls._engine = create_engine(
                    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}",
                    pool_pre_ping=True,
                    pool_recycle=300,
                    echo=echo,
                )
            elif engine in ["sqlite"]:
                cls._engine = create_engine("sqlite:///data/base.db", echo=True)
        return cls._engine

    @classmethod
    def get_map(cls, map_name: str, city: str) -> Union[Map, None]:
        """
        Gets a map from a given city
        :param map_name: The name of the map
        :param city: The name of the city
        :return: The corresponding map object or None if no map is available
        """
        with db_session(cls.init_engine()) as session:
            return (
                session.query(Map)
                .join(Region, Map.region_id == Region.region_id)
                .join(City, Region.city_id == City.city_id)
                .filter(City.name.like(city))
                .filter(Map.name.like(map_name))
                .first()
            )

    @classmethod
    def get_cities(cls) -> Union[list[City], None]:
        """
        Gets a list of cities
        :return: The list of cities or None if no cities were found
        """
        with db_session(cls.init_engine()) as session:
            return session.query(City).all()

    @classmethod
    def get_regions(cls, city_name) -> Union[list[Region], None]:
        """
        Gets a list of regions
        :param city_name: The name of the city
        :return: The list of regions or None if no regions were found
        """
        with db_session(cls.init_engine()) as session:
            return (
                session.query(Region)
                .join(City, City.city_id == Region.city_id)
                .filter(City.name.like(city_name))
                .all()
            )

    @classmethod
    def get_addresses(cls, city=None) -> Union[list[Address], None]:
        """
        Gets a list of addresses
        :param city: The name of the city
        :return: The list of addresses or None if no addresses were found
        """
        with db_session(cls.init_engine()) as session:
            if city is None:
                return session.query(Address).all()
            else:
                return (
                    session.query(Address)
                    .join(Map, Address.map_id == Map.map_id)
                    .join(Region, Region.region_id == Map.region_id)
                    .join(City, City.city_id == Region.city_id)
                    .filter(City.name.like(city))
                    .all()
                )

    @classmethod
    def get_maps(cls, city: str = None, region: str = None) -> Union[list[Map], None]:
        """
        Gets a list of maps
        :param city: The name of the city
        :param region: The name of the region
        :return: The list of maps or None if no maps were found
        """
        with db_session(cls.init_engine()) as session:
            if city is None:
                return session.query(Map).all()
            elif not region:
                return (
                    session.query(Map)
                    .join(Region, Region.region_id == Map.region_id)
                    .join(City, City.city_id == Region.city_id)
                    .filter(City.name.like(city))
                    .all()
                )
            else:
                return (
                    session.query(Map)
                    .join(Region, Region.region_id == Map.region_id)
                    .join(City, City.city_id == Region.city_id)
                    .filter(City.name.like(city))
                    .filter(Region.name.like(region))
                    .all()
                )

    @classmethod
    def get_matches_map(cls, address: Tuple[str, str], city) -> Union[Map, None]:
        """
        Gets the matches map for a given address and city
        :param address: The address
        :param city: The city
        :return: The map or None if no matches
        """
        with db_session(cls.init_engine()) as session:
            return (
                session.query(Address)
                .join(Map, Map.map_id == Address.map_id)
                .join(Region, Region.region_id == Map.region_id)
                .join(City, City.city_id == Region.city_id)
                .filter(City.name.like(city))
                .filter(Address.street.like(address[0]))
                .filter(Address.number.like(address[1]))
                .first()
                .map
            )

    @classmethod
    def _collect_maps_zip_xlsx(cls, zip_filepath, xlsx_filepath, city_name):
        """
        Collects all the maps from a zip file and extracts them
        :param zip_filepath: The path to the zip file
        :param xlsx_filepath: The path to the xlsx file
        :param city_name: The name of the city to extract
        """
        def unpack_zip(
            filepath, city_name
        ) -> Dict[str, Dict[str, Dict[str, Dict[str, Union[bytes, list]]]]]:
            """
            Unpacks the zip file into a dictionary
            :param filepath: The path to the zip file
            :param city_name: The name of the city to extract
            :return: A dictionary containing the extracted data
            """
            maps = {city_name: {}}
            with ZipFile(filepath) as archive:
                for file in filter(
                    lambda filename: filename.endswith(".png"), archive.namelist()
                ):
                    region = Path(file).parent.name
                    if region not in maps.get(city_name):
                        maps[city_name][region] = {}
                    maps[city_name][region][Path(file).stem] = {
                        "picture": archive.read(file),
                        "addresses": [],
                    }
            return maps

        maps = unpack_zip(zip_filepath, city_name)
        excel_table = load_workbook(xlsx_filepath)

        for city_regions in maps.values():
            for region, region_maps in city_regions.items():
                for map_name, map_values in region_maps.items():

                    map_addresses = list(
                        map(
                            lambda row: list(map(lambda cell: cell.value, row))[1:8],
                            filter(
                                lambda row: row[0].value
                                and row[0].value.lower() == map_name.lower(),
                                excel_table[region].iter_rows(),
                            ),
                        )
                    )
                    for i in range(len(map_addresses.copy())):
                        try:
                            map_addresses[i] = [
                                *map_addresses[i][:5],
                                map_addresses[i][6],
                            ]
                        except IndexError:
                            map_addresses[i] = [*map_addresses[i][:5], None]
                        for j in range(len(map_addresses[i])):
                            if element := map_addresses[i][j]:
                                if isinstance(element, datetime.datetime):
                                    map_addresses[i][
                                        j
                                    ] = f"{element.day}/{element.month}"
                                if str(element).strip() == "-":
                                    map_addresses[i][j] = None
                                else:
                                    map_addresses[i][j] = str(map_addresses[i][j])

                    map_values["addresses"] = map_addresses
        return maps

    @classmethod
    def create_city(cls, city, zip_filepath, xlsx_filepath):
        """
        Create a new city file with the given data.
        :param city: The city to create
        :param zip_filepath: The path to the zip file
        :param xlsx_filepath: The path to the xlsx file
        """
        with db_session(cls.init_engine(), mode="w") as session:
            maps = cls._collect_maps_zip_xlsx(zip_filepath, xlsx_filepath, city)

            for city, city_regions in maps.items():
                session.add(City(city))
                for city_region, region_maps in city_regions.items():
                    session.add(
                        Region(
                            city_region,
                            session.query(City).filter_by(name=city).first().city_id,
                        ),
                    )
                    for region_map_number, region_map_vals in region_maps.items():
                        session.add(
                            Map(
                                region_map_number,
                                region_map_vals.get("picture"),
                                session.query(Region)
                                .filter_by(
                                    name=city_region,
                                    city_id=session.query(City)
                                    .filter_by(name=city)
                                    .first()
                                    .city_id,
                                )
                                .first()
                                .region_id,
                            )
                        )
                        for address in region_map_vals.get("addresses"):
                            session.add(
                                Address(
                                    address[0],
                                    address[1],
                                    address[2],
                                    address[3],
                                    address[4],
                                    session.query(Map)
                                    .filter_by(
                                        name=region_map_number,
                                        region_id=session.query(Region)
                                        .filter_by(
                                            name=city_region,
                                            city_id=session.query(City)
                                            .filter_by(name=city)
                                            .first()
                                            .city_id,
                                        )
                                        .first()
                                        .region_id,
                                    )
                                    .first()
                                    .map_id,
                                    None,
                                    address[5],
                                )
                            )

        # cls._session.commit()
