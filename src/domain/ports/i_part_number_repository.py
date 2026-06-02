from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.entities.part_number import PartNumber


class IPartNumberRepository(ABC):

    @abstractmethod
    def get_by_id(self, part_num: str) -> PartNumber | None: ...

    @abstractmethod
    def get_all(self) -> list[PartNumber]: ...

    @abstractmethod
    def save(self, part_number: PartNumber) -> None: ...

    @abstractmethod
    def delete(self, part_num: str) -> None: ...
