import json
import os
import random

# def find_closest


def get_rand_map() -> str:
    regions = os.listdir(os.path.dirname(__file__) + "/src/flyers/")
    maps_files = [
        os.listdir(os.path.dirname(__file__) + "/src/flyers/" + reg + "/")
        for reg in regions
    ]
    map_code = random.choice(random.choice(maps_files)).split(".")[0]
    return map_code


def get_map_picture(map_code) -> str:
    map_file = ""
    for root, _, files in os.walk(os.path.dirname(__file__) + "/src/flyers/"):
        if f"{map_code}.png" in files:
            map_file = os.path.join(root, f"{map_code}.png")
    return map_file


def get_map_addresses(map_code) -> list:
    addrs = []
    resp = {}
    with open("regions.json", "r") as f:
        resp = dict(json.load(f))
    for map_range in resp["valueRanges"]:
        if map_code[0] == map_range["range"].split("!")[0].strip("'")[0]:
            for val in map_range["values"]:
                if map_code in val:
                    addrs.append(val)
    return addrs
