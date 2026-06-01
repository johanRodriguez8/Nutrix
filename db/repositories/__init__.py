"""Repository layer.

Every SQL statement in the app lives in one of these repository classes.
UI and domain code calls named methods instead of embedding SQL, so the
schema is touched in exactly one place per table.

Import the ready-made singletons:

    from db.repositories import parts_repo, conveyors_repo
"""
from db.repositories.conveyors_repository import ConveyorsRepository
from db.repositories.parts_repository import PartsRepository
from db.repositories.current_parts_repository import CurrentPartsRepository
from db.repositories.history_repository import HistoryRepository
from db.repositories.programs_repository import ProgramsRepository
from db.repositories.sequences_repository import SequencesRepository
from db.repositories.part_numbers_repository import PartNumbersRepository
from db.repositories.work_orders_repository import WorkOrdersRepository

conveyors_repo = ConveyorsRepository()
parts_repo = PartsRepository()
current_parts_repo = CurrentPartsRepository()
history_repo = HistoryRepository()
programs_repo = ProgramsRepository()
sequences_repo = SequencesRepository()
part_numbers_repo = PartNumbersRepository()
work_orders_repo = WorkOrdersRepository()

__all__ = [
    "conveyors_repo", "parts_repo", "current_parts_repo", "history_repo",
    "programs_repo", "sequences_repo", "part_numbers_repo", "work_orders_repo",
]
