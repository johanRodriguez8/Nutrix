from __future__ import annotations
from src.domain.ports.i_program_repository import IProgramRepository
from src.domain.entities.program import Program


class ProgramService:
    def __init__(self, programs: IProgramRepository):
        self._programs = programs

    def list_all(self, ascending: bool = True) -> list[Program]:
        programs = self._programs.get_all()
        return sorted(programs, key=lambda p: p.program_id, reverse=not ascending)

    def get(self, program_id: str) -> Program | None:
        return self._programs.get_by_id(program_id)

    def save(self, program: Program) -> None:
        if len(program.program_id) != 3:
            raise ValueError("Program ID must be exactly 3 characters.")
        self._programs.save(program)

    def delete(self, program_id: str) -> None:
        self._programs.delete(program_id)

    def list_ids(self) -> list[str]:
        rows = self._programs.all_ids()
        return [r[0] for r in rows] if rows else []
