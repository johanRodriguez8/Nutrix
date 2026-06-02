from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.entities.conveyor import Conveyor


class IConveyorRepository(ABC):

    @abstractmethod
    def get_by_id(self, hanger_id: int) -> Conveyor | None: ...

    @abstractmethod
    def get_by_hanger(self, hanger_num: int, conveyor: str) -> Conveyor | None: ...

    @abstractmethod
    def get_by_conveyor(self, conveyor: str) -> list[Conveyor]: ...

    @abstractmethod
    def get_all(self) -> list[Conveyor]: ...

    @abstractmethod
    def save(self, conveyor: Conveyor) -> None: ...

    @abstractmethod
    def delete(self, hanger_id: int) -> None: ...
