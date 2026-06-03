from src.infrastructure.db.connection import db
from src.infrastructure.config.settings import settings

def initialize():
    db.backup()
    _create_users()
    _seed_users()
    _create_programs()
    _create_sequences()
    _create_sequence_steps()
    _create_part_numbers()
    _create_work_orders()
    _create_part_instances()
    _create_conveyors()
    _create_history()
    _seed_conveyors()

def _create_users():
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            role      TEXT DEFAULT 'user'
        )
    """)


def _create_programs():
    db.execute("""
        CREATE TABLE IF NOT EXISTS programs (
            program_id     TEXT PRIMARY KEY,
            path           TEXT DEFAULT '',
            robot_num      TEXT NOT NULL,
            conveyor_start TEXT DEFAULT NULL,
            conveyor_end   TEXT DEFAULT NULL
        )
    """)


def _create_sequences():
    db.execute("""
        CREATE TABLE IF NOT EXISTS sequences (
            sequence_id TEXT PRIMARY KEY NOT NULL
        )
    """)


def _create_sequence_steps():
    db.execute("""
        CREATE TABLE IF NOT EXISTS sequence_steps (
            sequence_id     TEXT    NOT NULL,
            step            INTEGER NOT NULL,
            program_id      TEXT    NOT NULL,
            min_drying_time TEXT    NOT NULL,
            max_drying_time TEXT    NOT NULL,
            PRIMARY KEY (sequence_id, step),
            FOREIGN KEY (sequence_id) REFERENCES sequences(sequence_id),
            FOREIGN KEY (program_id)  REFERENCES programs(program_id)
        )
    """)


def _create_part_numbers():
    db.execute("""
        CREATE TABLE IF NOT EXISTS partNumbers (
            part_num    TEXT PRIMARY KEY NOT NULL,
            sequence_id TEXT DEFAULT NULL,
            FOREIGN KEY (sequence_id) REFERENCES sequences(sequence_id)
                DEFERRABLE INITIALLY DEFERRED
        )
    """)


def _create_work_orders():
    db.execute("""
        CREATE TABLE IF NOT EXISTS workOrders (
            order_id   TEXT    NOT NULL,
            part_num   TEXT    NOT NULL,
            customer   TEXT    DEFAULT NULL,
            target_qty INTEGER DEFAULT NULL,
            PRIMARY KEY (order_id, part_num),
            FOREIGN KEY (part_num) REFERENCES partNumbers(part_num)
        )
    """)


def _create_part_instances():
    db.execute("""
        CREATE TABLE IF NOT EXISTS part_instances (
            part_id          TEXT    PRIMARY KEY,
            part_num         TEXT    NOT NULL,
            order_id         TEXT    DEFAULT NULL,
            current_step     INTEGER DEFAULT NULL,
            program_id       TEXT    DEFAULT NULL,
            state            TEXT    DEFAULT 'IDLE',
            start_datetime   TEXT    NOT NULL,
            end_datetime     TEXT    DEFAULT NULL,
            run_time         TEXT    DEFAULT '00:00',
            station          TEXT    DEFAULT NULL,
            hanger_id        INTEGER DEFAULT NULL,
            hanger_end       TEXT    DEFAULT NULL,
            time_deviation   TEXT    DEFAULT '00:00',
            current_hanger   TEXT    DEFAULT NULL,
            current_conveyor TEXT    DEFAULT NULL,
            FOREIGN KEY (part_num)  REFERENCES partNumbers(part_num),
            FOREIGN KEY (order_id, part_num) REFERENCES workOrders(order_id, part_num)
                DEFERRABLE INITIALLY DEFERRED,
            FOREIGN KEY (program_id) REFERENCES programs(program_id),
            FOREIGN KEY (hanger_id)  REFERENCES conveyors(hanger_id)
                DEFERRABLE INITIALLY DEFERRED
        )
    """)


def _create_conveyors():
    db.execute("""
        CREATE TABLE IF NOT EXISTS conveyors (
            hanger_id  INTEGER PRIMARY KEY,
            hanger_num INTEGER NOT NULL,
            conveyor   TEXT    NOT NULL,
            status     TEXT    DEFAULT 'EMPTY',
            enable     INTEGER DEFAULT 1,
            part_id    TEXT    DEFAULT NULL,
            part_num   TEXT    DEFAULT NULL,
            order_id   TEXT    DEFAULT NULL,
            UNIQUE (hanger_num, conveyor),
            FOREIGN KEY (part_id)  REFERENCES part_instances(part_id)
                DEFERRABLE INITIALLY DEFERRED,
            FOREIGN KEY (part_num) REFERENCES partNumbers(part_num)
        )
    """)


def _create_history():
    db.execute("""
        CREATE TABLE IF NOT EXISTS history (
            part_id         TEXT    NOT NULL,
            step            INTEGER NOT NULL,
            part_num        TEXT    DEFAULT NULL,
            order_id        TEXT    DEFAULT NULL,
            program_id      TEXT    DEFAULT NULL,
            robot_num       TEXT    DEFAULT NULL,
            min_drying_time TEXT    DEFAULT NULL,
            max_drying_time TEXT    DEFAULT NULL,
            conveyor_start  TEXT    DEFAULT NULL,
            conveyor_end    TEXT    DEFAULT NULL,
            state           TEXT    DEFAULT 'IDLE',
            start_datetime  TEXT    DEFAULT NULL,
            end_datetime    TEXT    DEFAULT NULL,
            run_time        TEXT    DEFAULT '00:00',
            station         TEXT    DEFAULT NULL,
            hanger_id       INTEGER DEFAULT NULL,
            hanger_end      TEXT    DEFAULT NULL,
            time_deviation  TEXT    DEFAULT '00:00',
            upload_date     TEXT    DEFAULT NULL,
            PRIMARY KEY (part_id, step),
            FOREIGN KEY (program_id) REFERENCES programs(program_id),
            FOREIGN KEY (hanger_id)  REFERENCES conveyors(hanger_id)
        )
    """)


# ── seed data ─────────────────────────────────────────────────────────────────

def _seed_users():
    db.execute(
        "INSERT OR IGNORE INTO users (user_name, password, role) VALUES (?,?,?)",
        ("admin", settings.admin_password, "admin"),
    )
    db.execute(
        "INSERT OR IGNORE INTO users (user_name, password, role) VALUES (?,?,?)",
        ("user", "user", "user"),
    )


_CONVEYOR_HANGERS = {
    'A': 30,
    'B': 76,
    'C': 74,
    'D': 30,
}


def _seed_conveyors():
    hanger_id = 1
    for conveyor, total in _CONVEYOR_HANGERS.items():
        for hanger_num in range(1, total + 1):
            db.execute(
                "INSERT OR IGNORE INTO conveyors "
                "(hanger_id, hanger_num, conveyor) VALUES (?,?,?)",
                (hanger_id, hanger_num, conveyor),
            )
            hanger_id += 1
