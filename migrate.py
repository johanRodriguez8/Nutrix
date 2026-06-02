"""
One-shot migration: db/db.db (old schema) → db/db_new.db (new schema)

Run from the project root:
    python migrate.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD_PATH = ROOT / "db" / "db.db"
NEW_PATH = ROOT / "db" / "db_new.db"


# ── helpers ───────────────────────────────────────────────────────────────────

def _combine_dt(date_val, time_val):
    """Merge separate date + time columns into one datetime string."""
    _NULL_DATES = ('00/00/00', '', None)
    _NULL_TIMES = ('00:00', '', None)
    date = date_val if date_val not in _NULL_DATES else None
    time = time_val if time_val not in _NULL_TIMES else None
    if not date:
        return None
    return f"{date} {time}" if time else date


def _status_to_new(status: str) -> str:
    """Map old conveyor status values to new ConveyorStatus enum values."""
    return 'OCCUPIED' if status == 'FULL' else status


# ── schema ────────────────────────────────────────────────────────────────────

def _init_schema(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            role      TEXT DEFAULT 'user'
        );

        CREATE TABLE IF NOT EXISTS programs (
            program_id     TEXT PRIMARY KEY,
            path           TEXT DEFAULT '',
            robot_num      TEXT NOT NULL,
            conveyor_start TEXT DEFAULT NULL,
            conveyor_end   TEXT DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS sequences (
            sequence_id TEXT PRIMARY KEY NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sequence_steps (
            sequence_id     TEXT    NOT NULL,
            step            INTEGER NOT NULL,
            program_id      TEXT    NOT NULL,
            min_drying_time TEXT    NOT NULL,
            max_drying_time TEXT    NOT NULL,
            PRIMARY KEY (sequence_id, step),
            FOREIGN KEY (sequence_id) REFERENCES sequences(sequence_id),
            FOREIGN KEY (program_id)  REFERENCES programs(program_id)
        );

        CREATE TABLE IF NOT EXISTS partNumbers (
            part_num    TEXT PRIMARY KEY NOT NULL,
            sequence_id TEXT DEFAULT NULL,
            FOREIGN KEY (sequence_id) REFERENCES sequences(sequence_id)
                DEFERRABLE INITIALLY DEFERRED
        );

        CREATE TABLE IF NOT EXISTS workOrders (
            order_id   TEXT    NOT NULL,
            part_num   TEXT    NOT NULL,
            customer   TEXT    DEFAULT NULL,
            target_qty INTEGER DEFAULT NULL,
            PRIMARY KEY (order_id, part_num),
            FOREIGN KEY (part_num) REFERENCES partNumbers(part_num)
        );

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
            FOREIGN KEY (part_num)   REFERENCES partNumbers(part_num),
            FOREIGN KEY (program_id) REFERENCES programs(program_id),
            FOREIGN KEY (hanger_id)  REFERENCES conveyors(hanger_id)
                DEFERRABLE INITIALLY DEFERRED
        );

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
        );

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
        );
    """)
    print("  ✓ Schema created")


# ── table migrations ──────────────────────────────────────────────────────────

def _migrate_users(old, new):
    rows = old.execute("SELECT user_id, user_name, password, role FROM users").fetchall()
    new.executemany(
        "INSERT OR IGNORE INTO users (user_id, user_name, password, role) VALUES (?,?,?,?)",
        rows,
    )
    print(f"  ✓ users: {len(rows)} rows")


def _migrate_programs(old, new):
    rows = old.execute(
        "SELECT program_id, path, robot_num, conveyor_start, conveyor_end FROM programs"
    ).fetchall()
    new.executemany(
        "INSERT OR IGNORE INTO programs "
        "(program_id, path, robot_num, conveyor_start, conveyor_end) VALUES (?,?,?,?,?)",
        rows,
    )
    print(f"  ✓ programs: {len(rows)} rows")


def _migrate_sequences(old, new):
    rows = old.execute(
        "SELECT sequence_id, program_id, step, min_drying_time, max_drying_time FROM sequences"
    ).fetchall()
    # distinct sequence IDs → sequences table
    seen = set()
    seq_rows = []
    for row in rows:
        if row[0] not in seen:
            seen.add(row[0])
            seq_rows.append((row[0],))
    new.executemany("INSERT OR IGNORE INTO sequences (sequence_id) VALUES (?)", seq_rows)
    # all rows → sequence_steps (sequence_id, step, program_id, min, max)
    step_rows = [(r[0], r[2], r[1], r[3], r[4]) for r in rows]
    new.executemany(
        "INSERT OR IGNORE INTO sequence_steps "
        "(sequence_id, step, program_id, min_drying_time, max_drying_time) VALUES (?,?,?,?,?)",
        step_rows,
    )
    print(f"  ✓ sequences: {len(seq_rows)} sequences, {len(step_rows)} steps")


def _migrate_part_numbers(old, new):
    rows = old.execute("SELECT part_num, sequence_id FROM partNumbers").fetchall()
    new.executemany(
        "INSERT OR IGNORE INTO partNumbers (part_num, sequence_id) VALUES (?,?)", rows
    )
    print(f"  ✓ partNumbers: {len(rows)} rows")


def _migrate_work_orders(old, new):
    rows = old.execute(
        "SELECT order_id, part_num, customer, target_qty FROM workOrders"
    ).fetchall()
    # INSERT OR IGNORE handles duplicates from the old schema (no PK)
    new.executemany(
        "INSERT OR IGNORE INTO workOrders (order_id, part_num, customer, target_qty) "
        "VALUES (?,?,?,?)",
        rows,
    )
    print(f"  ✓ workOrders: {len(rows)} source rows (duplicates skipped)")


def _migrate_conveyors(old, new):
    rows = old.execute(
        "SELECT hanger_id, hanger_num, conveyor, status, enable, part_id, part_num, order_id "
        "FROM conveyors"
    ).fetchall()
    new_rows = [
        (r[0], r[1], r[2], _status_to_new(r[3]), r[4], r[5], r[6], r[7])
        for r in rows
    ]
    new.executemany(
        "INSERT OR IGNORE INTO conveyors "
        "(hanger_id, hanger_num, conveyor, status, enable, part_id, part_num, order_id) "
        "VALUES (?,?,?,?,?,?,?,?)",
        new_rows,
    )
    print(f"  ✓ conveyors: {len(new_rows)} rows")


def _migrate_part_instances(old, new):
    """Merge parts (status=1) + currentParts into part_instances."""
    parts = {
        r[0]: r for r in old.execute(
            "SELECT part_id, part_num, hanger_id, start_date, start_time, order_id "
            "FROM parts WHERE status = 1"
        ).fetchall()
    }
    current = {
        r[0]: r for r in old.execute("""
            SELECT part_id, part_num, current_step, program_id, state,
                   start_date, start_time, end_date, end_time,
                   run_time, station, hanger_id, hanger_end,
                   time_deviation, current_hanger, current_conveyor, order_id
            FROM currentParts
        """).fetchall()
    }
    new_rows = []
    for part_id, p in parts.items():
        c = current.get(part_id)
        if c:
            row = (
                part_id,
                c[1],                             # part_num
                c[16],                            # order_id
                c[2],                             # current_step
                c[3],                             # program_id
                c[4],                             # state
                _combine_dt(c[5], c[6]) or _combine_dt(p[3], p[4]) or '?',  # start_datetime
                _combine_dt(c[7], c[8]),          # end_datetime
                c[9] or '00:00',                  # run_time
                c[10],                            # station
                c[11] or p[2],                    # hanger_id
                c[12],                            # hanger_end
                c[13] or '00:00',                 # time_deviation
                c[14],                            # current_hanger
                c[15],                            # current_conveyor
            )
        else:
            row = (
                part_id,
                p[1],                             # part_num
                p[5],                             # order_id
                None,                             # current_step
                None,                             # program_id
                'IDLE',                           # state
                _combine_dt(p[3], p[4]) or '?',  # start_datetime
                None,                             # end_datetime
                '00:00',                          # run_time
                None,                             # station
                p[2],                             # hanger_id
                None,                             # hanger_end
                '00:00',                          # time_deviation
                None,                             # current_hanger
                None,                             # current_conveyor
            )
        new_rows.append(row)

    new.executemany(
        "INSERT OR IGNORE INTO part_instances "
        "(part_id, part_num, order_id, current_step, program_id, state, "
        "start_datetime, end_datetime, run_time, station, hanger_id, "
        "hanger_end, time_deviation, current_hanger, current_conveyor) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        new_rows,
    )
    skipped = len(parts) - len(new_rows)
    print(f"  ✓ part_instances: {len(new_rows)} rows "
          f"({len(current)} with active step, {len(parts)-len(current)} without)")
    if skipped:
        print(f"    ⚠ {skipped} rows skipped (duplicates)")


def _migrate_history(old, new):
    rows = old.execute("""
        SELECT part_id, part_num, step, program_id, robot_num,
               min_drying_time, max_drying_time, conveyor_start, conveyor_end,
               order_id, state, start_date, start_time, end_date, end_time,
               run_time, station, hanger_id, hanger_num, hanger_end,
               conveyor_start, conveyor_end, time_deviation, upload_date
        FROM history
    """).fetchall()
    new_rows = []
    seen = set()
    for r in rows:
        key = (r[0], r[2])          # (part_id, step)
        if key in seen:
            continue
        seen.add(key)
        new_rows.append((
            r[0],                   # part_id
            r[2],                   # step
            r[1],                   # part_num
            r[9],                   # order_id
            r[3],                   # program_id
            r[4],                   # robot_num
            r[5],                   # min_drying_time
            r[6],                   # max_drying_time
            r[7],                   # conveyor_start
            r[8],                   # conveyor_end
            r[10],                  # state
            _combine_dt(r[11], r[12]),  # start_datetime
            _combine_dt(r[13], r[14]),  # end_datetime
            r[15] or '00:00',       # run_time
            r[16],                  # station
            r[17],                  # hanger_id
            r[19],                  # hanger_end
            r[22] or '00:00',       # time_deviation
            r[23],                  # upload_date
        ))
    new.executemany(
        "INSERT OR IGNORE INTO history "
        "(part_id, step, part_num, order_id, program_id, robot_num, "
        "min_drying_time, max_drying_time, conveyor_start, conveyor_end, "
        "state, start_datetime, end_datetime, run_time, station, "
        "hanger_id, hanger_end, time_deviation, upload_date) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        new_rows,
    )
    dupes = len(rows) - len(new_rows)
    print(f"  ✓ history: {len(new_rows)} rows" +
          (f" ({dupes} duplicates skipped)" if dupes else ""))


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    if not OLD_PATH.exists():
        print(f"❌ Old database not found: {OLD_PATH}")
        sys.exit(1)
    if NEW_PATH.exists():
        print(f"❌ {NEW_PATH} already exists. Delete it first to re-run the migration.")
        sys.exit(1)

    print(f"Migrating {OLD_PATH} → {NEW_PATH}")
    old = sqlite3.connect(str(OLD_PATH))
    new = sqlite3.connect(str(NEW_PATH))
    new.execute("PRAGMA foreign_keys = OFF")

    try:
        _init_schema(new)
        _migrate_users(old, new)
        _migrate_programs(old, new)
        _migrate_sequences(old, new)
        _migrate_part_numbers(old, new)
        _migrate_work_orders(old, new)
        _migrate_conveyors(old, new)
        _migrate_part_instances(old, new)
        _migrate_history(old, new)
        new.commit()
        print("\n✅ Migration complete →", NEW_PATH)
    except Exception as e:
        new.rollback()
        NEW_PATH.unlink(missing_ok=True)
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        old.close()
        new.close()


if __name__ == "__main__":
    main()
