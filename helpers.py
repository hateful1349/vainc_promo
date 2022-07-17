import configparser
import json
import os


def read_config():
    config = configparser.ConfigParser()
    config.read(f"{os.path.dirname(__file__)}/configs/config.ini")
    return config


def set_chat_id(prom_id: str, chat_id: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][prom_id]["chat_id"] = chat_id
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def set_fname(prom_id: str, fname: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][prom_id] = {"lname": "", "phone": "", "address": "", "chat_id": "", "fname": fname}

    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def set_lname(prom_id: str, lname: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][prom_id]["lname"] = lname
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def set_phone(prom_id: str, phone: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][prom_id]["phone"] = phone
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def set_address(prom_id: str, addr: str):
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    db["range"][prom_id]["address"] = addr
    with open(db_file, "w", encoding="utf8") as f:
        json.dump(db, f, ensure_ascii=False)


def get_chat_id(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][prom_id]["chat_id"]


def get_fname(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][prom_id]["fname"]


def get_lname(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][prom_id]["lname"]


def get_phone(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][prom_id]["phone"]


def get_address(
    prom_id: str,
) -> str:
    db_file = read_config()["DB"]["db_file"]
    with open(db_file, "r") as f:
        db = json.load(f)
    return db["range"][prom_id]["address"]


def parse_callback_data(data):
    """
    Parse callback data into a dictionary.

    Args:
        data (str): Callback data to parse.

    Returns:
        dict: Dictionary of callback data.
    """
    fields = data.split("&")
    res = {"url": fields[0]}
    for field in fields[1:]:
        property, *args = field.split("=")
        res[property] = True if len(args) == 0 else args[0]
    return res
