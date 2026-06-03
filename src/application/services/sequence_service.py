from __future__ import annotations
from src.domain.ports.i_sequence_repository import ISequenceRepository
from src.domain.entities.sequence import Sequence, SequenceStep


class SequenceService:
    def __init__(self, sequences: ISequenceRepository):
        self._sequences = sequences

    def list_all(self) -> list[Sequence]:
        return self._sequences.get_all()

    def get(self, sequence_id: str) -> Sequence | None:
        return self._sequences.get_by_id(sequence_id)

    def save(self, sequence: Sequence) -> None:
        self._sequences.save(sequence)

    def delete(self, sequence_id: str) -> None:
        self._sequences.delete(sequence_id)

    def list_ids(self) -> list[str]:
        rows = self._sequences.distinct_ids()
        return [r[0] for r in rows] if rows else []

    def get_steps(self, sequence_id: str) -> list[SequenceStep]:
        return self._sequences.get_steps(sequence_id)
