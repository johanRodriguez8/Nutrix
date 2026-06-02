from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SequenceStep:
    sequence_id: str
    step: int
    program_id: str
    min_drying_time: str
    max_drying_time: str


@dataclass
class Sequence:
    sequence_id: str
    steps: list[SequenceStep] = field(default_factory=list)
