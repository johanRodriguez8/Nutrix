from collections import defaultdict

from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.domain.ports.i_sequence_repository import ISequenceRepository
from src.domain.entities.sequence import Sequence, SequenceStep

_STEP_COLUMNS = (
    "sequence_id, step, program_id, min_drying_time, max_drying_time"
)


class SequencesRepository(BaseRepository, ISequenceRepository):

    def _row_to_step(self, row) -> SequenceStep:
        sequence_id, step, program_id, min_dry, max_dry = row
        return SequenceStep(
            sequence_id=sequence_id,
            step=step,
            program_id=program_id,
            min_drying_time=min_dry,
            max_drying_time=max_dry,
        )

    # ── port interface ────────────────────────────────────────────────

    def get_by_id(self, sequence_id: str) -> Sequence | None:
        exists = self._db.query_scalar(
            "SELECT 1 FROM sequences WHERE sequence_id=?", (sequence_id,)
        )
        if not exists:
            return None
        rows = self._db.query(
            f"SELECT {_STEP_COLUMNS} FROM sequence_steps "
            "WHERE sequence_id=? ORDER BY step",
            (sequence_id,),
        ) or []
        return Sequence(
            sequence_id=sequence_id,
            steps=[self._row_to_step(r) for r in rows],
        )

    def get_all(self) -> list[Sequence]:
        seq_rows = self._db.query(
            "SELECT sequence_id FROM sequences ORDER BY sequence_id"
        ) or []
        if not seq_rows:
            return []
        step_rows = self._db.query(
            f"SELECT {_STEP_COLUMNS} FROM sequence_steps ORDER BY sequence_id, step"
        ) or []
        steps_by_seq: dict[str, list[SequenceStep]] = defaultdict(list)
        for row in step_rows:
            step = self._row_to_step(row)
            steps_by_seq[step.sequence_id].append(step)
        return [
            Sequence(sequence_id=row[0], steps=steps_by_seq[row[0]])
            for row in seq_rows
        ]

    def save(self, sequence: Sequence) -> None:
        self._db.execute(
            "INSERT OR IGNORE INTO sequences (sequence_id) VALUES (?)",
            (sequence.sequence_id,),
        )
        self._db.execute(
            "DELETE FROM sequence_steps WHERE sequence_id=?",
            (sequence.sequence_id,),
        )
        if sequence.steps:
            self._db.execute_many(
                f"INSERT INTO sequence_steps ({_STEP_COLUMNS}) VALUES (?,?,?,?,?)",
                [
                    (s.sequence_id, s.step, s.program_id,
                     s.min_drying_time, s.max_drying_time)
                    for s in sequence.steps
                ],
            )

    def delete(self, sequence_id: str) -> None:
        # sequence_steps rows are removed by FK cascade
        self._db.execute(
            "DELETE FROM sequences WHERE sequence_id=?", (sequence_id,)
        )

    # ── extra query methods ───────────────────────────────────────────

    def distinct_ids(self) -> list:
        return self._db.query(
            "SELECT sequence_id FROM sequences ORDER BY sequence_id"
        )

    def get_steps(self, sequence_id: str) -> list[SequenceStep]:
        rows = self._db.query(
            f"SELECT {_STEP_COLUMNS} FROM sequence_steps "
            "WHERE sequence_id=? ORDER BY step",
            (sequence_id,),
        ) or []
        return [self._row_to_step(r) for r in rows]
