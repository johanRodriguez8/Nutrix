from dataclasses import dataclass


@dataclass
class WorkOrder:
    order_id: str
    part_num: str
    customer: str | None = None
    target_qty: int | None = None
