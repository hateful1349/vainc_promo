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


class UserNotFoundException(Exception):
    def __init__(self, message=None):
        print(message or "User not found in users file")
