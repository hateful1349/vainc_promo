import configparser
import json
import os
from typing import Dict, List, Tuple


def read_config():
    config = configparser.ConfigParser()
    config.read(os.path.dirname(__file__) + "/configs/config.ini")
    return config


def collect_maps_codes(maps: dict) -> List[str]:
    res = []
    for rg_letter, rg in maps.items():
        for rg_number in rg.keys():
            res.append(rg_letter + rg_number)
    return res


def collect_addresses(maps: dict) -> List[str]:
    res = []
    for map_codes in maps.values():
        for mp in map_codes.values():
            for addr in mp["range"]:
                res.append(" ".join(addr))
    return res


def collect_maps(sheet_file) -> Dict[str, Dict[str, Dict[str, str | List[str]]]]:
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


def find_matches_map(address: str, maps: dict):
    for reg_letter, map_numbers in maps.items():
        for map_number, mp in map_numbers.items():
            if address in [" ".join(item) for item in mp["range"]]:
                return f"{reg_letter}{map_number}"


def get_map(mp: str, maps: dict) -> Tuple[str, List[str]]:
    map_file = maps[mp[0]][mp[1:]]["file"]
    map_addresses = maps[mp[0]][mp[1:]]["range"]
    return map_file, map_addresses


def set_chat_id(prom_id: str, chat_id: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][str(prom_id)]["chat_id"] = chat_id
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def set_fname(prom_id: str, fname: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][str(prom_id)] = {
        "fname": "",
        "lname": "",
        "phone": "",
        "address": "",
        "chat_id": "",
    }
    db["range"][str(prom_id)]["fname"] = fname
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def set_lname(prom_id: str, lname: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][str(prom_id)]["lname"] = lname
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def set_phone(prom_id: str, phone: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][str(prom_id)]["phone"] = phone
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def set_address(prom_id: str, addr: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][str(prom_id)]["address"] = addr
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def get_chat_id(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][str(prom_id)]["chat_id"]


def get_fname(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][str(prom_id)]["fname"]


def get_lname(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][str(prom_id)]["lname"]


def get_phone(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][str(prom_id)]["phone"]


def get_address(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][str(prom_id)]["address"]


class Singleton(type):
    """
    A singleton class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
