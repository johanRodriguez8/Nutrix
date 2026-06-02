from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.entities.user import User


class IUserRepository(ABC):

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_name(self, user_name: str) -> User | None: ...

    @abstractmethod
    def get_all(self) -> list[User]: ...

    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def delete(self, user_id: int) -> None: ...
