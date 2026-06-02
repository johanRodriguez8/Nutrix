from db.connection import db as _default_db


class BaseRepository:
    def __init__(self, db=None):
        self._db = db or _default_db
