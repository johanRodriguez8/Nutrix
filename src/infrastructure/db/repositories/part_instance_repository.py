from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.domain.ports.i_part_instance_repository import IPartInstanceRepository
from src.domain.entities.part_instance import PartInstance
from src.domain.value_objects.part_state import PartState

_COLUMNS = (
    "part_id, part_num, order_id, current_step, program_id, state, "
    "start_datetime, end_datetime, run_time, station, hanger_id, "
    "hanger_end, time_deviation, current_hanger, current_conveyor"
)


class PartInstanceRepository(BaseRepository, IPartInstanceRepository):

    def _to_entity(self, row) -> PartInstance:
        (part_id, part_num, order_id, current_step, program_id, state,
         start_dt, end_dt, run_time, station, hanger_id,
         hanger_end, time_dev, current_hanger, current_conveyor) = row
        return PartInstance(
            part_id=part_id,
            part_num=part_num,
            order_id=order_id,
            current_step=current_step,
            program_id=program_id,
            state=PartState(state) if state else PartState.IDLE,
            start_datetime=start_dt,
            end_datetime=end_dt,
            run_time=run_time or '00:00',
            station=station,
            hanger_id=hanger_id,
            hanger_end=hanger_end,
            time_deviation=time_dev or '00:00',
            current_hanger=current_hanger,
            current_conveyor=current_conveyor,
        )

    def _to_params(self, p: PartInstance) -> tuple:
        return (
            p.part_id, p.part_num, p.order_id, p.current_step, p.program_id,
            p.state.value, p.start_datetime, p.end_datetime, p.run_time,
            p.station, p.hanger_id, p.hanger_end, p.time_deviation,
            p.current_hanger, p.current_conveyor,
        )

    # ── port interface ────────────────────────────────────────────────

    def get_by_id(self, part_id: str) -> PartInstance | None:
        row = self._db.query_one(
            f"SELECT {_COLUMNS} FROM part_instances WHERE part_id=?", (part_id,)
        )
        return self._to_entity(row) if row else None

    def get_all(self) -> list[PartInstance]:
        rows = self._db.query(
            f"SELECT {_COLUMNS} FROM part_instances ORDER BY part_id"
        ) or []
        return [self._to_entity(r) for r in rows]

    def save(self, part_instance: PartInstance) -> None:
        self._db.execute(
            f"INSERT INTO part_instances ({_COLUMNS}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            self._to_params(part_instance),
        )

    def update(self, part_instance: PartInstance) -> None:
        p = part_instance
        self._db.execute(
            "UPDATE part_instances SET "
            "part_num=?, order_id=?, current_step=?, program_id=?, state=?, "
            "start_datetime=?, end_datetime=?, run_time=?, station=?, hanger_id=?, "
            "hanger_end=?, time_deviation=?, current_hanger=?, current_conveyor=? "
            "WHERE part_id=?",
            (p.part_num, p.order_id, p.current_step, p.program_id, p.state.value,
             p.start_datetime, p.end_datetime, p.run_time, p.station, p.hanger_id,
             p.hanger_end, p.time_deviation, p.current_hanger, p.current_conveyor,
             p.part_id),
        )

    def delete(self, part_id: str) -> None:
        self._db.execute("DELETE FROM part_instances WHERE part_id=?", (part_id,))

    # ── targeted write methods ────────────────────────────────────────

    def set_state(self, state: PartState, part_id: str) -> None:
        self._db.execute(
            "UPDATE part_instances SET state=? WHERE part_id=?",
            (state.value, part_id),
        )

    def set_location(self, current_hanger: str | None,
                     current_conveyor: str | None, part_id: str) -> None:
        self._db.execute(
            "UPDATE part_instances SET current_hanger=?, current_conveyor=? WHERE part_id=?",
            (current_hanger, current_conveyor, part_id),
        )

    def set_hanger(self, hanger_id: int | None, part_id: str) -> None:
        self._db.execute(
            "UPDATE part_instances SET hanger_id=? WHERE part_id=?",
            (hanger_id, part_id),
        )

    def set_step(self, current_step: int, part_id: str) -> None:
        self._db.execute(
            "UPDATE part_instances SET current_step=? WHERE part_id=?",
            (current_step, part_id),
        )

    def advance_to_step(self, part_id: str, current_step: int, program_id: str,
                        start_datetime: str, end_datetime: str, run_time: str,
                        station: str, hanger_id: int | None,
                        hanger_end: str | None, time_deviation: str) -> None:
        """Advance a part to a new step — replaces reset_to_ready + update_current_program."""
        self._db.execute(
            "UPDATE part_instances SET current_step=?, program_id=?, state=?, "
            "start_datetime=?, end_datetime=?, run_time=?, station=?, "
            "hanger_id=?, hanger_end=?, time_deviation=? "
            "WHERE part_id=?",
            (current_step, program_id, PartState.RUNNING.value,
             start_datetime, end_datetime, run_time, station,
             hanger_id, hanger_end, time_deviation, part_id),
        )

    # ── query methods ─────────────────────────────────────────────────

    def exists(self, part_id: str) -> bool:
        return self._db.query_scalar(
            "SELECT 1 FROM part_instances WHERE part_id=?", (part_id,)
        ) is not None

    def all_ids(self) -> list:
        return self._db.query(
            "SELECT DISTINCT part_id FROM part_instances ORDER BY part_id"
        )

    def unassigned_ids(self) -> list:
        return self._db.query(
            "SELECT part_id FROM part_instances WHERE hanger_id IS NULL ORDER BY part_id"
        )

    def get_by_state(self, *states: PartState) -> list[PartInstance]:
        placeholders = ','.join('?' for _ in states)
        rows = self._db.query(
            f"SELECT {_COLUMNS} FROM part_instances WHERE state IN ({placeholders})",
            tuple(s.value for s in states),
        ) or []
        return [self._to_entity(r) for r in rows]

    def get_program_location(self, part_id: str):
        return self._db.query_one(
            "SELECT program_id, current_hanger, current_conveyor "
            "FROM part_instances WHERE part_id=?",
            (part_id,),
        )
