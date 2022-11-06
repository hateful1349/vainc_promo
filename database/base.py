from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from loader import config

Base = declarative_base()


def init_engine(engine_type=None, echo=None):
    """
    Initializes the database engine

    :param engine_type: Database type using sqlite/sql/psql
    :param echo: Print or not
    :type echo: bool
    """
    engine = engine_type or config.db.dbtype
    if config.loglevel == "DEBUG":
        echo = True
    match engine:
        case "sql":
            return create_engine(
                f"mysql+pymysql://{config.db.user}"
                f":{config.db.password}"
                f"@{config.db.host}"
                f"/{config.db.dbname}",
                pool_pre_ping=True,
                pool_recycle=300,
                echo=echo,
            )
        case "psql":
            return create_engine(
                f"postgresql+psycopg2://{config.db.user}"
                f":{config.db.password}"
                f"@{config.db.host}"
                f"/{config.db.dbname}",
                echo=echo,
            )
        case "sqlite":
            return create_engine(f"sqlite:///{config.db.dbfile}", echo=echo)


@contextmanager
def db_session(engine_type=None, mode="r", echo=False):
    """
    Generates a session for the given engine

    :param engine_type: the engine to use
    :param mode: the mode to use ('w'/'r')
    :type mode: str
    :param echo: Print or not
    :type echo: bool
    """

    engine = init_engine(engine_type, echo)

    Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine)()
    try:
        yield session
        if mode == "w":
            session.commit()
    except:
        if echo:
            print("Some error, so rolling back database changes")
        session.rollback()
        raise
    finally:
        session.close()
