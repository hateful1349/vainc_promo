from contextlib import contextmanager
import datetime
from pathlib import Path
from typing import Tuple, Union
from zipfile import ZipFile

from data import config
from openpyxl import load_workbook
from specials.singleton import Singleton
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models.models import Address, City, Map, Region
# from database.models.city import City
# from database.models.region import Region
# from database.models.map import Map
# from database.models.address import Address


@contextmanager
def db_session(engine, mode="r"):
    # modes
    # r - only read from database
    # w - only write to database
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
    def init_session(cls, engine=None, echo=False) -> bool:
        if cls._engine is None:
            if engine is None or engine in ["sql"]:
                cls._engine = create_engine(
                    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}",
                    echo=echo,
                )
            elif engine in ["sqlite"]:
                cls._engine = create_engine("sqlite:///data/base.db", echo=True)
            # return sessionmaker(bind=engine)()
        return cls._engine
        # return bool(cls._engine)

    @classmethod
    def get_map(cls, map_name: str, city: str) -> Union[Map, None]:
        with db_session(cls.init_session()) as session:
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
        with db_session(cls.init_session()) as session:
            return session.query(City).all()

    @classmethod
    def get_addresses(cls, city=None) -> Union[list[Address], None]:
        with db_session(cls.init_session()) as session:
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
    def get_maps(cls, city: str = None) -> Union[list[Map], None]:
        with db_session(cls.init_session()) as session:
            if city is None:
                return session.query(Map).all()
            return (
                session.query(Map)
                .join(Region, Map.region_id == Region.region_id)
                .join(City, Region.city_id == City.city_id)
                .filter(City.name.like(city))
                .all()
            )

    @classmethod
    def get_matches_map(cls, address: Tuple[str, str], city) -> Union[Map, None]:
        with db_session(cls.init_session()) as session:
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
        def unpack_zip(filepath, city_name):
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
                        # "picture": "FUCKING BYTES",
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
        with db_session(cls.init_session()) as session:
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
                                    city_id=cls._session.query(City)
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
                                        region_id=cls._session.query(Region)
                                        .filter_by(
                                            name=city_region,
                                            city_id=cls._session.query(City)
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


# Database.create_city(
#     "Нижний Тагил",
#     "/home/god/Documents/bdsm/bdsm_promo/tools/Карты.zip",
#     "/home/god/Documents/bdsm/bdsm_promo/tools/База Нижний Тагил.xlsx",
# )
