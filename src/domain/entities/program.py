from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Program:
    program_id: str
    robot_num: str
    path: str = ''
    conveyor_start: str | None = None
    conveyor_end: str | None = None
