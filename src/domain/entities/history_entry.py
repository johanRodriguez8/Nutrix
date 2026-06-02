from __future__ import annotations
from dataclasses import dataclass
from src.domain.value_objects.part_state import PartState


@dataclass(frozen=True)
class HistoryEntry:
    part_id: str
    step: int
    part_num: str | None = None
    order_id: str | None = None
    program_id: str | None = None
    robot_num: str | None = None
    min_drying_time: str | None = None
    max_drying_time: str | None = None
    conveyor_start: str | None = None
    conveyor_end: str | None = None
    state: PartState = PartState.IDLE
    start_datetime: str | None = None
    end_datetime: str | None = None
    run_time: str = '00:00'
    station: str | None = None
    hanger_id: int | None = None
    hanger_end: str | None = None
    time_deviation: str = '00:00'
    upload_date: str | None = None
