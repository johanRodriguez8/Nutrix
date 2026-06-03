from __future__ import annotations
from src.domain.ports.i_work_order_repository import IWorkOrderRepository
from src.domain.entities.work_order import WorkOrder


class WorkOrderService:
    def __init__(self, work_orders: IWorkOrderRepository):
        self._work_orders = work_orders

    def list_all(self) -> list[WorkOrder]:
        return self._work_orders.get_all()

    def get(self, order_id: str, part_num: str) -> WorkOrder | None:
        return self._work_orders.get_by_id(order_id, part_num)

    def get_by_order(self, order_id: str) -> list[WorkOrder]:
        return self._work_orders.get_by_order(order_id)

    def save(self, work_order: WorkOrder) -> None:
        self._work_orders.save(work_order)

    def delete(self, order_id: str, part_num: str) -> None:
        self._work_orders.delete(order_id, part_num)

    def list_order_ids(self) -> list[str]:
        rows = self._work_orders.distinct_order_ids()
        return [r[0] for r in rows] if rows else []
