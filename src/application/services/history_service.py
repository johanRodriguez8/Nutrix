from __future__ import annotations
from src.domain.ports.i_history_repository import IHistoryRepository
from src.domain.entities.history_entry import HistoryEntry
from src.domain.value_objects.part_state import PartState


class HistoryService:
    def __init__(self, history: IHistoryRepository):
        self._history = history

    def get_all(self) -> list[HistoryEntry]:
        return self._history.get_all()

    def get_by_part(self, part_id: str) -> list[HistoryEntry]:
        return self._history.get_by_part(part_id)

    def get_step(self, part_id: str, step: int) -> HistoryEntry | None:
        return self._history.get_step(part_id, step)

    def record(self, entry: HistoryEntry) -> None:
        self._history.save(entry)

    def update_step(self, entry: HistoryEntry) -> None:
        self._history.update_step(entry)

    def mark_complete(self, part_id: str, end_datetime: str) -> None:
        self._history.mark_last_step_done(end_datetime, part_id)

    def set_state(self, part_id: str, step: int, state: PartState) -> None:
        self._history.set_state(state, part_id, step)

    def delete(self, part_id: str) -> None:
        self._history.delete(part_id)

    def list_part_ids(self) -> list[str]:
        rows = self._history.distinct_part_ids()
        return [r[0] for r in rows] if rows else []
