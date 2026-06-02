from __future__ import annotations
from dataclasses import dataclass
from src.domain.value_objects.conveyor_status import ConveyorStatus


@dataclass
class Conveyor:
    hanger_id: int
    hanger_num: int
    conveyor: str
    status: ConveyorStatus = ConveyorStatus.EMPTY
    enable: bool = True
    part_id: str | None = None
    part_num: str | None = None
    order_id: str | None = None
