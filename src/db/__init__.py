from typing import Final

import peewee
from playhouse.pool import PooledSqliteDatabase

proxy = peewee.DatabaseProxy()

CONFIG: Final[dict] = {
    'foreign_keys': 1,
}

PATH_TO_DB: Final[str] = "./static/app.db"


def init(testing=False):
    path = ':memory:' if testing else PATH_TO_DB
    proxy.initialize(PooledSqliteDatabase(path, pragmas=CONFIG, check_same_thread=False))

    project_models = peewee.Model.__subclasses__()[1:]
    with proxy:
        proxy.create_tables(project_models)
