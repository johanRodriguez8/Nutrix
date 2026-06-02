from dataclasses import dataclass, field


@dataclass
class User:
    user_name: str
    password: str
    role: str = 'user'
    user_id: int | None = field(default=None)
