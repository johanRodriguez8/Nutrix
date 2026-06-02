from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.domain.ports.i_conveyor_repository import IConveyorRepository
from src.domain.entities.conveyor import Conveyor
from src.domain.value_objects.conveyor_status import ConveyorStatus


class ConveyorsRepository(BaseRepository, IConveyorRepository):

    def _to_entity(self, row) -> Conveyor:
        hanger_id, hanger_num, conveyor, status, enable, part_id, part_num, order_id = row
        return Conveyor(
            hanger_id=hanger_id,
            hanger_num=hanger_num,
            conveyor=conveyor,
            status=ConveyorStatus(status),
            enable=bool(enable),
            part_id=part_id,
            part_num=part_num,
            order_id=order_id,
        )

    _SELECT = (
        "SELECT hanger_id, hanger_num, conveyor, status, enable, part_id, part_num, order_id "
        "FROM conveyors"
    )

    # ── port interface ────────────────────────────────────────────────

    def get_by_id(self, hanger_id: int) -> Conveyor | None:
        row = self._db.query_one(f"{self._SELECT} WHERE hanger_id=?", (hanger_id,))
        return self._to_entity(row) if row else None

    def get_by_hanger(self, hanger_num: int, conveyor: str) -> Conveyor | None:
        row = self._db.query_one(
            f"{self._SELECT} WHERE hanger_num=? AND conveyor=?", (hanger_num, conveyor)
        )
        return self._to_entity(row) if row else None

    def get_by_conveyor(self, conveyor: str) -> list[Conveyor]:
        rows = self._db.query(
            f"{self._SELECT} WHERE conveyor=? ORDER BY hanger_num", (conveyor,)
        ) or []
        return [self._to_entity(r) for r in rows]

    def get_all(self) -> list[Conveyor]:
        rows = self._db.query(f"{self._SELECT} ORDER BY conveyor, hanger_num") or []
        return [self._to_entity(r) for r in rows]

    def save(self, conveyor: Conveyor) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO conveyors "
            "(hanger_id, hanger_num, conveyor, status, enable, part_id, part_num, order_id) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (conveyor.hanger_id, conveyor.hanger_num, conveyor.conveyor,
             conveyor.status.value, int(conveyor.enable),
             conveyor.part_id, conveyor.part_num, conveyor.order_id),
        )

    def delete(self, hanger_id: int) -> None:
        self._db.execute("DELETE FROM conveyors WHERE hanger_id=?", (hanger_id,))

    # ── extra write methods ───────────────────────────────────────────

    def free(self, hanger_num: int, conveyor: str) -> None:
        """Empty a hanger, leaving order_id untouched."""
        self._db.execute(
            "UPDATE conveyors SET status=?, part_id=NULL, part_num=NULL "
            "WHERE conveyor=? AND hanger_num=?",
            (ConveyorStatus.EMPTY.value, conveyor, hanger_num),
        )

    def clear(self, hanger_num: int, conveyor: str) -> None:
        """Fully empty a hanger including its order_id."""
        self._db.execute(
            "UPDATE conveyors SET part_id=NULL, part_num=NULL, status=?, order_id=NULL "
            "WHERE hanger_num=? AND conveyor=?",
            (ConveyorStatus.EMPTY.value, hanger_num, conveyor),
        )

    def fill(self, part_id: str, part_num: str, hanger_num: int, conveyor: str) -> None:
        self._db.execute(
            "UPDATE conveyors SET part_id=?, part_num=?, status=? "
            "WHERE hanger_num=? AND conveyor=?",
            (part_id, part_num, ConveyorStatus.OCCUPIED.value, hanger_num, conveyor),
        )

    def fill_with_order(self, part_id: str, part_num: str, order_id: str,
                        hanger_num: int, conveyor: str) -> None:
        self._db.execute(
            "UPDATE conveyors SET status=?, part_id=?, part_num=?, order_id=? "
            "WHERE hanger_num=? AND conveyor=?",
            (ConveyorStatus.OCCUPIED.value, part_id, part_num, order_id, hanger_num, conveyor),
        )

    def set_enable(self, enable: bool, hanger_num: int, conveyor: str) -> None:
        self._db.execute(
            "UPDATE conveyors SET enable=? WHERE hanger_num=? AND conveyor=?",
            (int(enable), hanger_num, conveyor),
        )

    def set_part_id(self, part_id: str | None, hanger_num: int, conveyor: str) -> None:
        status = ConveyorStatus.OCCUPIED.value if part_id else ConveyorStatus.EMPTY.value
        self._db.execute(
            "UPDATE conveyors SET part_id=?, status=? WHERE hanger_num=? AND conveyor=?",
            (part_id, status, hanger_num, conveyor),
        )

    def insert_hanger(self, hanger_id: int, hanger_num: int,
                      conveyor: str, part_id: str | None = None) -> None:
        self._db.execute(
            "INSERT OR IGNORE INTO conveyors(hanger_id, hanger_num, conveyor, part_id) "
            "VALUES (?,?,?,?)",
            (hanger_id, hanger_num, conveyor, part_id),
        )

    # ── extra query methods ───────────────────────────────────────────

    def empty_hangers(self, conveyor: str):
        return self._db.query(
            "SELECT hanger_num, status FROM conveyors WHERE conveyor=? AND status=?",
            (conveyor, ConveyorStatus.EMPTY.value),
        )

    def hangers_by_status(self, status: ConveyorStatus, conveyor: str):
        return self._db.query(
            "SELECT hanger_num FROM conveyors WHERE status=? AND conveyor=?",
            (status.value, conveyor),
        )
