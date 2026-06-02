"""Managed SQLite connection.

Single place that owns how we talk to the database: every query goes
through one short-lived, properly committed/rolled-back connection, and
backups happen *explicitly* (startup / shutdown / on demand) instead of
on every write.
"""
import shutil
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from src.infrastructure.config.settings import settings

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = str(_PROJECT_ROOT / "db" / "db.db")
_BACKUP_FOLDER = str(_PROJECT_ROOT / "db" / "backups")
Path(_BACKUP_FOLDER).mkdir(parents=True, exist_ok=True)


class Database:
    """Thin, thread-safe access layer over a SQLite file.

    A fresh connection is opened per operation (safe across the Qt /
    robot worker threads) and always closed. Writes commit on success
    and roll back on failure. Backups are never triggered automatically
    by a write — call :meth:`backup` when you actually want one.
    """

    def __init__(self, path: str = DB_PATH):
        self.path = path

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, query, params=None):
        """Run a write/DDL statement. Returns affected row count."""
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query, params or ())
                return cur.rowcount
        except Exception as e:
            print(f"❌ Error al ejecutar la consulta: {e}")
            return 0

    def execute_many(self, query, seq_of_params):
        try:
            with self._connect() as conn:
                conn.cursor().executemany(query, seq_of_params)
        except Exception as e:
            print(f"❌ Error al ejecutar la consulta: {e}")

    def query(self, query, params=None):
        """Run a SELECT and return all rows (or ``None`` on error)."""
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(query, params or ())
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Error al ejecutar la consulta: {e}")
            return None

    def query_one(self, query, params=None):
        """Run a SELECT and return the first row, or ``None``."""
        rows = self.query(query, params)
        return rows[0] if rows else None

    def query_scalar(self, query, params=None):
        """Return the first column of the first row, or ``None``."""
        row = self.query_one(query, params)
        return row[0] if row else None

    def drop_table(self, name):
        self.execute(f"DROP TABLE {name}")

    def backup(self):
        """Copy the DB file to the shared folder and a local backups dir."""
        import os
        if not os.path.exists(self.path):
            print("⚠️ No se encontró la base de datos para respaldar.")
            return
        backup_filename = "db_backup.db"
        try:
            shared = str(Path(settings.backup_shared_folder) / backup_filename)
            shutil.copyfile(self.path, shared)
        except Exception as e:
            print(f"⚠️ No se pudo respaldar en carpeta compartida: {e}")
        shutil.copyfile(self.path, str(Path(_BACKUP_FOLDER) / backup_filename))


db = Database()
