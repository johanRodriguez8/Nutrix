from __future__ import annotations
from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.domain.ports.i_part_number_repository import IPartNumberRepository
from src.domain.entities.part_number import PartNumber


class PartNumbersRepository(BaseRepository, IPartNumberRepository):

    def _to_entity(self, row) -> PartNumber:
        part_num, sequence_id = row
        return PartNumber(part_num=part_num, sequence_id=sequence_id)

    # ── port interface ────────────────────────────────────────────────

    def get_by_id(self, part_num: str) -> PartNumber | None:
        row = self._db.query_one(
            "SELECT part_num, sequence_id FROM partNumbers WHERE part_num=?", (part_num,)
        )
        return self._to_entity(row) if row else None

    def get_all(self) -> list[PartNumber]:
        rows = self._db.query(
            "SELECT part_num, sequence_id FROM partNumbers ORDER BY part_num"
        ) or []
        return [self._to_entity(r) for r in rows]

    def save(self, part_number: PartNumber) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO partNumbers (part_num, sequence_id) VALUES (?,?)",
            (part_number.part_num, part_number.sequence_id),
        )

    def delete(self, part_num: str) -> None:
        self._db.execute("DELETE FROM partNumbers WHERE part_num=?", (part_num,))

    # ── extra query methods ───────────────────────────────────────────

    def get_sequence_id(self, part_num: str) -> str | None:
        return self._db.query_scalar(
            "SELECT sequence_id FROM partNumbers WHERE part_num=?", (part_num,)
        )

    def all_part_nums(self):
        return self._db.query("SELECT part_num FROM partNumbers")

    def distinct_part_nums(self):
        return self._db.query(
            "SELECT DISTINCT part_num FROM partNumbers ORDER BY part_num"
        )

    def list_all_ordered(self, ascending=True):
        order = "ASC" if ascending else "DESC"
        return self._db.query(
            f"SELECT part_num, sequence_id FROM partNumbers ORDER BY sequence_id {order}"
        )

    def update(self, part_num: str, sequence_id: str, old_part_num: str) -> None:
        self._db.execute(
            "UPDATE partNumbers SET part_num=?, sequence_id=? WHERE part_num=?",
            (part_num, sequence_id, old_part_num),
        )
