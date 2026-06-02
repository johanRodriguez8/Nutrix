from abc import ABC, abstractmethod
from src.domain.entities.work_order import WorkOrder


class IWorkOrderRepository(ABC):

    @abstractmethod
    def get_by_id(self, order_id: str, part_num: str) -> WorkOrder | None: ...

    @abstractmethod
    def get_by_order(self, order_id: str) -> list[WorkOrder]: ...

    @abstractmethod
    def get_all(self) -> list[WorkOrder]: ...

    @abstractmethod
    def save(self, work_order: WorkOrder) -> None: ...

    @abstractmethod
    def delete(self, order_id: str, part_num: str) -> None: ...
