from db.repositories.base_repository import BaseRepository


class WorkOrdersRepository(BaseRepository):
    def distinct_order_ids(self):
        return self._db.query("SELECT DISTINCT order_id FROM workOrders ORDER BY order_id")
