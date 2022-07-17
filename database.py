import json
import os
from functools import reduce

from yadisk import YaDisk, exceptions

from exceptions import API_FILE, ApiTypeError, TokenError
from helpers import read_config
from specials import Singleton


class Sheet(metaclass=Singleton):
    """
    Class for working with the Google/Yandex tables
    It is used to receive and send the necessary information in the table
    """

    def __yandex_connect(self):
        # check token in config file
        config = read_config()
        token = dict(config).get("YANDEX_API").get("oauth_token")
        if token is None:
            raise TokenError("Can't read oauth_token from config file")

        # check if the token is valid
        disk = YaDisk(token=token)
        if not disk.check_token():
            raise TokenError("Can't connect to Yandex Disk API with your oauth_token")

        self._connection = True
        self._obj = "YANDEX"

        # downloading file
        # check if file for download is specified
        wanted_file = dict(config).get("YANDEX_API").get("wanted_file")
        if wanted_file is None:
            raise API_FILE
        try:
            disk.download(
                wanted_file,
                os.path.dirname(__file__)
                + dict(config).get("COMMON").get("sheet_file"),
            )
        except exceptions.PathNotFoundError:
            print("Not found requested file in yandex disk")
            os.remove(
                os.path.dirname(__file__) + dict(config).get("COMMON").get("sheet_file")
            )

    def __google_connect(self):
        print("Deprecated because of google's policy. Please use Yandex instead.")

    _connection = None
    _obj = None
    _supported_api = {
        "google": {
            "short": ["g"],
            "connection": __google_connect,
        },
        "yandex": {
            "short": ["y"],
            "connection": __yandex_connect,
        },
    }

    @classmethod
    def connect(cls, api_type: str):
        """
        Check connection and download base

        :type argument for Google or Yandex API
        available types - (g)oogle | (y)andex
        """
        if cls._connection is not None:
            return
        api_type = api_type.lower()
        if api_type not in set(cls._supported_api.keys()) | set(
            reduce(
                lambda a, b: a + b,
                map(lambda v: v["short"], cls._supported_api.values()),
            )
        ):
            raise ApiTypeError
        connection_func = None
        if cls._supported_api.get(api_type):
            connection_func = cls._supported_api[api_type]["connection"]
        else:
            for v in cls._supported_api.values():
                if api_type in v["short"]:
                    connection_func = v["connection"]
                    break
        connection_func(cls)

    @classmethod
    def get_connection(cls):
        return cls._obj


class SheetParser(metaclass=Singleton):
    _file = None

    def __init__(cls, file: str = None) -> None:
        super().__init__()
        # if cls._file is None:
        #     if file is None:
        #         config = read_config()
        #         file = dict(config).get("COMMON").get("sheet_file")
        #     cls._file = file
        if cls._file is None:
            cls._file = file or "pzpfkdsfsd"

    @classmethod
    def set_file(cls, file: str = None) -> None:
        cls._file = file

    @classmethod
    def get_file(cls):
        return cls._file


class Database(metaclass=Singleton):
    _maps = None
    _addresses = None
    _map_codes = None
    _cities = None

    @classmethod
    def get_maps(cls):
        if cls._maps:
            return cls._maps
        cities = os.listdir(os.path.join(os.path.dirname(__file__), "src"))
        maps = {}
        for city in cities:
            with open(
                os.path.join(os.path.dirname(__file__), "src", city, "regions.json")
            ) as f:
                sheet = json.load(f)
            maps[city] = {}
            for region in sheet["valueRanges"]:
                map_letter = region["range"].split("!")[0].strip("'")[0]
                maps[city][map_letter] = {}
                for line in region["values"][1:]:
                    if str(reduce(lambda a, b: a + b, line, "")).strip() != "":
                        map_number = line[0][1:]
                        if map_number not in maps[city][map_letter]:
                            map_file = os.path.join(
                                os.path.dirname(__file__),
                                "src",
                                city,
                                "flyers",
                                f"{map_letter}АО",
                                f"{map_letter}{map_number}.png",
                            )
                            maps[city][map_letter][map_number] = {
                                "file": map_file,
                                "range": [],
                            }
                        address = (line[1], line[2])
                        maps[city][map_letter][map_number]["range"].append(address)
        cls._maps = maps
        return cls._maps

    @classmethod
    def get_addresses(cls):
        if cls._addresses:
            return cls._addresses
        if cls._maps is None:
            cls.get_maps()
        res = {}
        for city, map_letters in cls._maps.items():
            res[city] = []
            for map_numbers in map_letters.values():
                for addresses in map(lambda v: v["range"], map_numbers.values()):
                    res[city] += list(map(lambda l: (" ".join(l)).lower(), addresses))
        cls._addresses = res
        return cls._addresses

    @classmethod
    def get_maps_codes(cls):
        if cls._map_codes:
            return cls._map_codes
        if cls._maps is None:
            cls.get_maps()
        res = {}
        for city, map_letters in cls._maps.items():
            res[city] = []
            for map_letter, map_numbers in map_letters.items():
                res[city] += list(
                    map(
                        lambda map_number: f"{map_letter}{map_number}",
                        map_numbers.keys(),
                    )
                )

        cls._map_codes = res
        return cls._map_codes

    @classmethod
    def get_cities(cls):
        if cls._cities:
            return cls._cities
        if cls._maps is None:
            cls.get_maps()
        cls._cities = list(cls._maps.keys())
        return cls._cities

    @classmethod
    def find_matches_map(cls, address: str, city: str):
        if cls._maps is None:
            cls.get_maps()
        for reg_letter, map_numbers in cls._maps[city].items():
            for map_number, mp in map_numbers.items():
                if address.lower() in [
                    (" ".join(item)).lower() for item in mp["range"]
                ]:
                    return f"{reg_letter}{map_number}"

    @classmethod
    def get_map(cls, mp: str, city: str):
        if cls._maps is None:
            cls.get_maps()
        map_file = cls._maps[city][mp[0]][mp[1:]]["file"]
        map_addresses = cls._maps[city][mp[0]][mp[1:]]["range"]
        return map_file, map_addresses

    @classmethod
    def update(cls):
        cls._maps = None
        cls._map_codes = None
        cls._addresses = None
        cls._cities = None
