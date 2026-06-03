from __future__ import annotations
from src.domain.ports.i_part_number_repository import IPartNumberRepository
from src.domain.entities.part_number import PartNumber


class PartNumberService:
    def __init__(self, part_numbers: IPartNumberRepository):
        self._part_numbers = part_numbers

    def list_all(self, ascending: bool = True) -> list[PartNumber]:
        part_numbers = self._part_numbers.get_all()
        return sorted(part_numbers, key=lambda p: p.part_num, reverse=not ascending)

    def get(self, part_num: str) -> PartNumber | None:
        return self._part_numbers.get_by_id(part_num)

    def save(self, part_number: PartNumber) -> None:
        self._part_numbers.save(part_number)

    def update(self, new_part_num: str, sequence_id: str | None, old_part_num: str) -> None:
        self._part_numbers.update(new_part_num, sequence_id, old_part_num)

    def delete(self, part_num: str) -> None:
        self._part_numbers.delete(part_num)

    def list_nums(self) -> list[str]:
        rows = self._part_numbers.all_part_nums()
        return [r[0] for r in rows] if rows else []
