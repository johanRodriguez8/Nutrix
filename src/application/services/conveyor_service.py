from __future__ import annotations
from src.domain.ports.i_conveyor_repository import IConveyorRepository
from src.domain.entities.conveyor import Conveyor
from src.domain.value_objects.conveyor_status import ConveyorStatus


class ConveyorService:
    def __init__(self, conveyors: IConveyorRepository):
        self._conveyors = conveyors

    def list_all(self) -> list[Conveyor]:
        return self._conveyors.get_all()

    def get_by_conveyor(self, conveyor: str) -> list[Conveyor]:
        return self._conveyors.get_by_conveyor(conveyor)

    def get_hanger(self, hanger_num: int, conveyor: str) -> Conveyor | None:
        return self._conveyors.get_by_hanger(hanger_num, conveyor)

    def get_by_id(self, hanger_id: int) -> Conveyor | None:
        return self._conveyors.get_by_id(hanger_id)

    def assign_part(self, part_id: str, part_num: str,
                    hanger_num: int, conveyor: str) -> None:
        self._conveyors.fill(part_id, part_num, hanger_num, conveyor)

    def assign_part_with_order(self, part_id: str, part_num: str, order_id: str,
                               hanger_num: int, conveyor: str) -> None:
        self._conveyors.fill_with_order(part_id, part_num, order_id, hanger_num, conveyor)

    def free_hanger(self, hanger_num: int, conveyor: str) -> None:
        """Remove part from hanger but keep order_id."""
        self._conveyors.free(hanger_num, conveyor)

    def clear_hanger(self, hanger_num: int, conveyor: str) -> None:
        """Fully empty hanger including order_id."""
        self._conveyors.clear(hanger_num, conveyor)

    def set_hanger_enabled(self, hanger_num: int, conveyor: str, enable: bool) -> None:
        self._conveyors.set_enable(enable, hanger_num, conveyor)

    def add_hanger(self, hanger_id: int, hanger_num: int, conveyor: str,
                   part_id: str | None = None) -> None:
        self._conveyors.insert_hanger(hanger_id, hanger_num, conveyor, part_id)

    def remove_hanger(self, hanger_id: int) -> None:
        self._conveyors.delete(hanger_id)

    def save(self, conveyor: Conveyor) -> None:
        self._conveyors.save(conveyor)

    def empty_hangers(self, conveyor: str) -> list:
        return self._conveyors.empty_hangers(conveyor)

    def hangers_by_status(self, status: ConveyorStatus, conveyor: str) -> list:
        return self._conveyors.hangers_by_status(status, conveyor)
