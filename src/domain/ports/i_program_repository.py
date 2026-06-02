from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.entities.program import Program


class IProgramRepository(ABC):

    @abstractmethod
    def get_by_id(self, program_id: str) -> Program | None: ...

    @abstractmethod
    def get_all(self) -> list[Program]: ...

    @abstractmethod
    def save(self, program: Program) -> None: ...

    @abstractmethod
    def delete(self, program_id: str) -> None: ...
