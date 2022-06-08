import configparser
import json
import os
from typing import Tuple


def read_config():
    config = configparser.ConfigParser()
    config.read(os.path.dirname(__file__) + "/configs/config.ini")
    return config


def collect_maps_codes(maps: dict):
    res = []
    for rg_letter, rg in maps.items():
        for rg_number in rg.keys():
            res.append(f"{rg_letter}{rg_number}")
    return res


def collect_addrs(maps: dict):
    res = []
    for map_codes in maps.values():
        for _, mp in map_codes.items():
            for addr in mp["range"]:
                res.append(" ".join(addr))
    return res


def collect_maps(sheet_file):
    sheet = dict()
    with open(sheet_file, "r") as f:
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


def get_map(mp:str, maps: dict) -> Tuple[str, list]:
    map_file = maps[mp[0]][mp[1:]]["file"]
    map_addrs = maps[mp[0]][mp[1:]]["range"]
    return map_file, map_addrs