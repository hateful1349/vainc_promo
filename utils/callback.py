from typing import Dict, Union


def parse_callback_data(data: str) -> Dict[str, Union[str, bool]]:
    """
    Parses a callback data into a dictionary.

    :param data: Callback data
    :type data: str
    :return: Dictionary of callback data
    """
    fields = data.split("&")
    res = {"url": fields[0]}
    for field in fields[1:]:
        property, *args = field.split("=")
        res[property] = True if len(args) == 0 else args[0]
    return res
