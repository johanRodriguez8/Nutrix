from __future__ import annotations
from src.domain.ports.i_part_instance_repository import IPartInstanceRepository
from src.domain.entities.part_instance import PartInstance
from src.domain.value_objects.part_state import PartState


class PartTrackingService:
    def __init__(self, part_instances: IPartInstanceRepository):
        self._part_instances = part_instances

    def get_all(self) -> list[PartInstance]:
        return self._part_instances.get_all()

    def get(self, part_id: str) -> PartInstance | None:
        return self._part_instances.get_by_id(part_id)

    def exists(self, part_id: str) -> bool:
        return self._part_instances.exists(part_id)

    def register(self, part_instance: PartInstance) -> None:
        if self._part_instances.exists(part_instance.part_id):
            raise ValueError(f"Part '{part_instance.part_id}' is already registered.")
        self._part_instances.save(part_instance)

    def update(self, part_instance: PartInstance) -> None:
        self._part_instances.update(part_instance)

    def set_state(self, part_id: str, state: PartState) -> None:
        self._part_instances.set_state(state, part_id)

    def set_location(self, part_id: str, current_hanger: str | None,
                     current_conveyor: str | None) -> None:
        self._part_instances.set_location(current_hanger, current_conveyor, part_id)

    def advance_step(self, part_id: str, current_step: int, program_id: str,
                     start_datetime: str, end_datetime: str, run_time: str,
                     station: str, hanger_id: int | None, hanger_end: str | None,
                     time_deviation: str) -> None:
        self._part_instances.advance_to_step(
            part_id, current_step, program_id, start_datetime, end_datetime,
            run_time, station, hanger_id, hanger_end, time_deviation,
        )

    def delete(self, part_id: str) -> None:
        self._part_instances.delete(part_id)

    def get_by_state(self, *states: PartState) -> list[PartInstance]:
        return self._part_instances.get_by_state(*states)

    def get_unassigned_ids(self) -> list[str]:
        rows = self._part_instances.unassigned_ids()
        return [r[0] for r in rows] if rows else []

    def list_ids(self) -> list[str]:
        rows = self._part_instances.all_ids()
        return [r[0] for r in rows] if rows else []
