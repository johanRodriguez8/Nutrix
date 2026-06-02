from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.entities.part_instance import PartInstance


class IPartInstanceRepository(ABC):

    @abstractmethod
    def get_by_id(self, part_id: str) -> PartInstance | None: ...

    @abstractmethod
    def get_all(self) -> list[PartInstance]: ...

    @abstractmethod
    def save(self, part_instance: PartInstance) -> None: ...

    @abstractmethod
    def update(self, part_instance: PartInstance) -> None: ...

    @abstractmethod
    def delete(self, part_id: str) -> None: ...
