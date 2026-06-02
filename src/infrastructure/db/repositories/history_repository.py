from __future__ import annotations
from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.domain.ports.i_history_repository import IHistoryRepository
from src.domain.entities.history_entry import HistoryEntry
from src.domain.value_objects.part_state import PartState

_COLUMNS = (
    "part_id, step, part_num, order_id, program_id, robot_num, "
    "min_drying_time, max_drying_time, conveyor_start, conveyor_end, "
    "state, start_datetime, end_datetime, run_time, station, "
    "hanger_id, hanger_end, time_deviation, upload_date"
)


class HistoryRepository(BaseRepository, IHistoryRepository):

    def _to_entity(self, row) -> HistoryEntry:
        (part_id, step, part_num, order_id, program_id, robot_num,
         min_drying, max_drying, conv_start, conv_end,
         state, start_dt, end_dt, run_time, station,
         hanger_id, hanger_end, time_dev, upload_date) = row
        return HistoryEntry(
            part_id=part_id,
            step=step,
            part_num=part_num,
            order_id=order_id,
            program_id=program_id,
            robot_num=robot_num,
            min_drying_time=min_drying,
            max_drying_time=max_drying,
            conveyor_start=conv_start,
            conveyor_end=conv_end,
            state=PartState(state) if state else PartState.IDLE,
            start_datetime=start_dt,
            end_datetime=end_dt,
            run_time=run_time or '00:00',
            station=station,
            hanger_id=hanger_id,
            hanger_end=hanger_end,
            time_deviation=time_dev or '00:00',
            upload_date=upload_date,
        )

    # ── port interface ────────────────────────────────────────────────

    def get_by_part(self, part_id: str) -> list[HistoryEntry]:
        rows = self._db.query(
            f"SELECT {_COLUMNS} FROM history WHERE part_id=? ORDER BY step",
            (part_id,),
        ) or []
        return [self._to_entity(r) for r in rows]

    def get_all(self) -> list[HistoryEntry]:
        rows = self._db.query(
            f"SELECT {_COLUMNS} FROM history ORDER BY part_id, step"
        ) or []
        return [self._to_entity(r) for r in rows]

    def save(self, entry: HistoryEntry) -> None:
        self._db.execute(
            f"INSERT OR IGNORE INTO history ({_COLUMNS}) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (entry.part_id, entry.step, entry.part_num, entry.order_id,
             entry.program_id, entry.robot_num, entry.min_drying_time,
             entry.max_drying_time, entry.conveyor_start, entry.conveyor_end,
             entry.state.value, entry.start_datetime, entry.end_datetime,
             entry.run_time, entry.station, entry.hanger_id,
             entry.hanger_end, entry.time_deviation, entry.upload_date),
        )

    # ── extra write methods ───────────────────────────────────────────

    def update_step(self, entry: HistoryEntry) -> None:
        self._db.execute(
            "UPDATE history SET program_id=?, robot_num=?, min_drying_time=?, "
            "max_drying_time=?, state=?, start_datetime=?, end_datetime=?, run_time=?, "
            "station=?, hanger_id=?, hanger_end=?, conveyor_start=?, conveyor_end=?, "
            "time_deviation=? WHERE part_id=? AND step=?",
            (entry.program_id, entry.robot_num, entry.min_drying_time,
             entry.max_drying_time, entry.state.value, entry.start_datetime,
             entry.end_datetime, entry.run_time, entry.station, entry.hanger_id,
             entry.hanger_end, entry.conveyor_start, entry.conveyor_end,
             entry.time_deviation, entry.part_id, entry.step),
        )

    def set_time_deviation(self, time_dev: str, part_id: str, step: int) -> None:
        self._db.execute(
            "UPDATE history SET time_deviation=? WHERE part_id=? AND step=?",
            (time_dev, part_id, step),
        )

    def set_state(self, state: PartState, part_id: str, step: int) -> None:
        self._db.execute(
            "UPDATE history SET state=? WHERE part_id=? AND step=?",
            (state.value, part_id, step),
        )

    def mark_last_step_done(self, end_datetime: str, part_id: str) -> None:
        self._db.execute(
            "UPDATE history SET end_datetime=?, state=? "
            "WHERE part_id=? AND step=(SELECT MAX(step) FROM history WHERE part_id=?)",
            (end_datetime, PartState.COMPLETE.value, part_id, part_id),
        )

    def delete(self, part_id: str) -> None:
        self._db.execute("DELETE FROM history WHERE part_id=?", (part_id,))

    # ── extra query methods ───────────────────────────────────────────

    def distinct_part_ids(self):
        return self._db.query(
            "SELECT DISTINCT part_id FROM history ORDER BY part_id"
        )

    def get_step(self, part_id: str, step: int) -> HistoryEntry | None:
        row = self._db.query_one(
            f"SELECT {_COLUMNS} FROM history WHERE part_id=? AND step=?",
            (part_id, step),
        )
        return self._to_entity(row) if row else None

    def distinct_order_id(self, part_id: str):
        return self._db.query(
            "SELECT DISTINCT order_id FROM history WHERE part_id=?", (part_id,)
        )

    def distinct_part_num(self, part_id: str):
        return self._db.query(
            "SELECT DISTINCT part_num FROM history WHERE part_id=?", (part_id,)
        )

    def get_last_end_datetime(self, part_id: str) -> str | None:
        return self._db.query_scalar(
            "SELECT end_datetime FROM history "
            "WHERE step=(SELECT MAX(step) FROM history WHERE part_id=?) AND part_id=?",
            (part_id, part_id),
        )
