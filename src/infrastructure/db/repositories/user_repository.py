from __future__ import annotations
from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.domain.ports.i_user_repository import IUserRepository
from src.domain.entities.user import User


class UserRepository(BaseRepository, IUserRepository):

    def _to_entity(self, row) -> User:
        user_id, user_name, password, role = row
        return User(user_name=user_name, password=password, role=role, user_id=user_id)

    def get_by_id(self, user_id: int) -> User | None:
        row = self._db.query_one(
            "SELECT user_id, user_name, password, role FROM users WHERE user_id=?",
            (user_id,),
        )
        return self._to_entity(row) if row else None

    def get_by_name(self, user_name: str) -> User | None:
        row = self._db.query_one(
            "SELECT user_id, user_name, password, role FROM users WHERE user_name=?",
            (user_name,),
        )
        return self._to_entity(row) if row else None

    def get_all(self) -> list[User]:
        rows = self._db.query(
            "SELECT user_id, user_name, password, role FROM users ORDER BY user_name"
        ) or []
        return [self._to_entity(r) for r in rows]

    def save(self, user: User) -> None:
        if user.user_id is None:
            self._db.execute(
                "INSERT INTO users (user_name, password, role) VALUES (?,?,?)",
                (user.user_name, user.password, user.role),
            )
        else:
            self._db.execute(
                "INSERT OR REPLACE INTO users (user_id, user_name, password, role) VALUES (?,?,?,?)",
                (user.user_id, user.user_name, user.password, user.role),
            )

    def delete(self, user_id: int) -> None:
        self._db.execute("DELETE FROM users WHERE user_id=?", (user_id,))
