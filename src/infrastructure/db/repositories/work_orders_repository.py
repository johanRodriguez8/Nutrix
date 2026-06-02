from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.domain.ports.i_work_order_repository import IWorkOrderRepository
from src.domain.entities.work_order import WorkOrder


class WorkOrdersRepository(BaseRepository, IWorkOrderRepository):

    def _to_entity(self, row) -> WorkOrder:
        order_id, part_num, customer, target_qty = row
        return WorkOrder(
            order_id=order_id,
            part_num=part_num,
            customer=customer,
            target_qty=target_qty,
        )

    # ── port interface ────────────────────────────────────────────────

    def get_by_id(self, order_id: str, part_num: str) -> WorkOrder | None:
        row = self._db.query_one(
            "SELECT order_id, part_num, customer, target_qty "
            "FROM workOrders WHERE order_id=? AND part_num=?",
            (order_id, part_num),
        )
        return self._to_entity(row) if row else None

    def get_by_order(self, order_id: str) -> list[WorkOrder]:
        rows = self._db.query(
            "SELECT order_id, part_num, customer, target_qty "
            "FROM workOrders WHERE order_id=? ORDER BY part_num",
            (order_id,),
        ) or []
        return [self._to_entity(r) for r in rows]

    def get_all(self) -> list[WorkOrder]:
        rows = self._db.query(
            "SELECT order_id, part_num, customer, target_qty "
            "FROM workOrders ORDER BY order_id, part_num"
        ) or []
        return [self._to_entity(r) for r in rows]

    def save(self, work_order: WorkOrder) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO workOrders (order_id, part_num, customer, target_qty) "
            "VALUES (?,?,?,?)",
            (work_order.order_id, work_order.part_num,
             work_order.customer, work_order.target_qty),
        )

    def delete(self, order_id: str, part_num: str) -> None:
        self._db.execute(
            "DELETE FROM workOrders WHERE order_id=? AND part_num=?",
            (order_id, part_num),
        )

    # ── extra query methods ───────────────────────────────────────────

    def distinct_order_ids(self) -> list:
        return self._db.query(
            "SELECT DISTINCT order_id FROM workOrders ORDER BY order_id"
        )

    def delete_by_order(self, order_id: str) -> None:
        self._db.execute(
            "DELETE FROM workOrders WHERE order_id=?", (order_id,)
        )
