from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")

USERS_DB_FILE = env.str("USERS_DB_FILE")

with env.prefixed("DB_"):
    DB_HOST = env.str("HOST")
    DB_USER = env.str("USER")
    DB_PASSWORD = env.str("PASSWORD")
    DB_NAME = env.str("NAME")

