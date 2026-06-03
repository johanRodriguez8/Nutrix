from __future__ import annotations
from src.domain.ports.i_user_repository import IUserRepository
from src.domain.entities.user import User


class AuthService:
    def __init__(self, users: IUserRepository):
        self._users = users

    def authenticate(self, username: str, password: str) -> User | None:
        user = self._users.get_by_name(username)
        if user and user.password == password:
            return user
        return None

    def create_user(self, username: str, password: str, role: str = 'user') -> User:
        existing = self._users.get_by_name(username)
        if existing:
            raise ValueError(f"User '{username}' already exists.")
        user = User(user_name=username, password=password, role=role)
        self._users.save(user)
        return self._users.get_by_name(username)

    def change_password(self, username: str, new_password: str) -> None:
        user = self._users.get_by_name(username)
        if not user:
            raise ValueError(f"User '{username}' not found.")
        user.password = new_password
        self._users.save(user)

    def list_users(self) -> list[User]:
        return self._users.get_all()

    def delete_user(self, user_id: int) -> None:
        self._users.delete(user_id)
