from __future__ import annotations
from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.domain.ports.i_program_repository import IProgramRepository
from src.domain.entities.program import Program


class ProgramsRepository(BaseRepository, IProgramRepository):

    def _to_entity(self, row) -> Program:
        program_id, path, robot_num, conveyor_start, conveyor_end = row
        return Program(
            program_id=program_id,
            path=path or '',
            robot_num=robot_num,
            conveyor_start=conveyor_start,
            conveyor_end=conveyor_end,
        )

    # ── port interface ────────────────────────────────────────────────

    def get_by_id(self, program_id: str) -> Program | None:
        row = self._db.query_one(
            "SELECT program_id, path, robot_num, conveyor_start, conveyor_end "
            "FROM programs WHERE program_id=?",
            (program_id,),
        )
        return self._to_entity(row) if row else None

    def get_all(self) -> list[Program]:
        rows = self._db.query(
            "SELECT program_id, path, robot_num, conveyor_start, conveyor_end "
            "FROM programs ORDER BY program_id"
        ) or []
        return [self._to_entity(r) for r in rows]

    def save(self, program: Program) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO programs "
            "(program_id, path, robot_num, conveyor_start, conveyor_end) VALUES (?,?,?,?,?)",
            (program.program_id, program.path, program.robot_num,
             program.conveyor_start, program.conveyor_end),
        )

    def delete(self, program_id: str) -> None:
        self._db.execute("DELETE FROM programs WHERE program_id=?", (program_id,))

    # ── extra query methods ───────────────────────────────────────────

    def get_path_and_conveyors(self, program_id):
        return self._db.query_one(
            "SELECT path, conveyor_start, conveyor_end FROM programs WHERE program_id=?",
            (program_id,),
        )

    def get_robot_and_conveyors(self, program_id):
        return self._db.query_one(
            "SELECT robot_num, conveyor_start, conveyor_end FROM programs WHERE program_id=?",
            (program_id,),
        )

    def get_robot(self, program_id):
        return self._db.query_scalar(
            "SELECT robot_num FROM programs WHERE program_id=?", (program_id,)
        )

    def all_ids(self):
        return self._db.query("SELECT program_id FROM programs ORDER BY program_id")

    def update_basic(self, new_program_id, path, robot_num, program_id):
        self._db.execute(
            "UPDATE programs SET program_id=?, path=?, robot_num=? WHERE program_id=?",
            (new_program_id, path, robot_num, program_id),
        )
