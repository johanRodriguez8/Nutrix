from dataclasses import dataclass
from src.domain.value_objects.part_state import PartState


@dataclass
class PartInstance:
    part_id: str
    part_num: str
    start_datetime: str
    order_id: str | None = None
    current_step: int | None = None
    program_id: str | None = None
    state: PartState = PartState.IDLE
    end_datetime: str | None = None
    run_time: str = '00:00'
    station: str | None = None
    hanger_id: int | None = None
    hanger_end: str | None = None
    time_deviation: str = '00:00'
    current_hanger: str | None = None
    current_conveyor: str | None = None
