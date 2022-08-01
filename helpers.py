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
