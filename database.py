import json
import os
from functools import reduce
from typing import Dict, List, Tuple

from yadisk import YaDisk, exceptions

from helpers import Singleton, read_config


class ApiTypeError(Exception):
    def __init__(self):
        print("Wrong API type")


class TokenError(Exception):
    def __init__(self, message=None):
        if message is None:
            print(
                "Something with the token. Please check your oauth_token under YANDEX_API section in the configs/config.ini file."
            )
        else:
            print(message)


class API_FILE(Exception):
    def __init__(self, message=None):
        if message is None:
            print(
                "You need to specify required file in config file under YANDEX_API/wanted_file."
            )
        else:
            print(message)


class Sheet(metaclass=Singleton):
    """
    Class for working with the Google/Yandex tables
    It is used to receive and send the necessary information in the table
    """

    def __yandex_connect(cls):
        # check token in config file
        config = read_config()
        token = dict(config).get("YANDEX_API").get("oauth_token")
        if token is None:
            raise TokenError("Can't read oauth_token from config file")

        # check if the token is valid
        disk = YaDisk(token=token)
        if not disk.check_token():
            raise TokenError("Can't connect to Yandex Disk API with your oauth_token")

        cls._connection = True
        cls._obj = "YANDEX"

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

    def __google_connect(cls):
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
        api_type = api_type.lower()
        if cls._connection is None:
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
    _maps = None
    _addresses = None
    _map_codes = None

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

    @classmethod
    def collect_maps_codes(maps: dict) -> List[str]:
        res = []
        for rg_letter, rg in maps.items():
            for rg_number in rg.keys():
                res.append(rg_letter + rg_number)
        return res

    @classmethod
    def collect_addresses(maps: dict) -> List[str]:
        res = []
        for map_codes in maps.values():
            for mp in map_codes.values():
                for addr in mp["range"]:
                    res.append(" ".join(addr))
        return res

    @classmethod
    def collect_maps(sheet_file) -> Dict[str, Dict[str, Dict[str, str | List[str]]]]:
        # sheet = dict()
        with open(sheet_file) as f:
            sheet = json.load(f)
        maps = dict()
        for region in sheet["valueRanges"]:
            map_letter = region["range"].split("!")[0].strip("'")[0]
            maps[map_letter] = dict()
            for line in region["values"][1:]:
                if len(line) > 0:
                    map_number = line[0][1:]
                    if map_number not in maps[map_letter]:
                        file = f"{map_letter}{map_number}.png"
                        folder = os.path.dirname(__file__)
                        folder += f"/src/flyers/{map_letter}АО/"
                        map_file = folder + file
                        maps[map_letter][map_number] = {}
                        maps[map_letter][map_number]["file"] = map_file
                        maps[map_letter][map_number]["range"] = []
                    addr = (line[1], line[2])
                    maps[map_letter][map_number]["range"].append(addr)
        return maps

    @classmethod
    def find_matches_map(address: str, maps: dict):
        for reg_letter, map_numbers in maps.items():
            for map_number, mp in map_numbers.items():
                if address in [" ".join(item) for item in mp["range"]]:
                    return f"{reg_letter}{map_number}"

    @classmethod
    def get_map(mp: str, maps: dict) -> Tuple[str, List[str]]:
        map_file = maps[mp[0]][mp[1:]]["file"]
        map_addresses = maps[mp[0]][mp[1:]]["range"]
        return map_file, map_addresses


print(SheetParser.set_file())
print(SheetParser.get_file())
print(SheetParser.set_file("jsdjsjd"))
print(SheetParser.get_file())
print(SheetParser.get_file())
s = SheetParser()
print(s.get_file())
print(SheetParser.set_file())
print(SheetParser.get_file())
# print(SheetParser().get_file())
