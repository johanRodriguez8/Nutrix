from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PartNumber:
    part_num: str
    sequence_id: str | None = None
