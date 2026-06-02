from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.entities.history_entry import HistoryEntry


class IHistoryRepository(ABC):

    @abstractmethod
    def get_by_part(self, part_id: str) -> list[HistoryEntry]: ...

    @abstractmethod
    def get_all(self) -> list[HistoryEntry]: ...

    @abstractmethod
    def save(self, entry: HistoryEntry) -> None: ...
