from abc import ABC, abstractmethod
from src.domain.entities.sequence import Sequence


class ISequenceRepository(ABC):

    @abstractmethod
    def get_by_id(self, sequence_id: str) -> Sequence | None: ...

    @abstractmethod
    def get_all(self) -> list[Sequence]: ...

    @abstractmethod
    def save(self, sequence: Sequence) -> None: ...

    @abstractmethod
    def delete(self, sequence_id: str) -> None: ...
