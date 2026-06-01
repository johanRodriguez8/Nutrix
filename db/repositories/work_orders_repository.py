"""All SQL touching the ``workOrders`` table."""
from db.connection import db


class WorkOrdersRepository:
    def distinct_order_ids(self):
        return db.query("SELECT DISTINCT order_id FROM workOrders ORDER BY order_id")
