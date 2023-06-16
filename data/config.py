from dataclasses import dataclass

from environs import Env


@dataclass
class Bot:
    token: str


@dataclass
class DB:
    dbname: str | None
    user: str | None
    password: str | None
    host: str | None
    dbfile: str | None
    dbtype: str | None


@dataclass
class Config:
    bot: Bot
    db: DB
    loglevel: str
    address_search_count: int


def load_config():
    env = Env()
    env.read_env()

    def load_db():
        with env.prefixed("DB_"):
            return (
                env.str("NAME"),
                env.str("USER"),
                env.str("PASSWORD"),
                env.str("HOST"),
                env.str("FILE"),
                env.str("TYPE"),
            )

    return Config(
        bot=Bot(token=env.str("BOT_TOKEN")),
        db=DB(*load_db()),
        loglevel=env.str("LOGLEVEL").upper(),
        address_search_count=env.int("ADDRESS_SEARCH_COUNT"),
    )
