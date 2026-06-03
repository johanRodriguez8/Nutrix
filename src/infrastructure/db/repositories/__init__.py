from src.infrastructure.db.repositories.programs_repository import ProgramsRepository
from src.infrastructure.db.repositories.part_numbers_repository import PartNumbersRepository
from src.infrastructure.db.repositories.conveyors_repository import ConveyorsRepository
from src.infrastructure.db.repositories.history_repository import HistoryRepository
from src.infrastructure.db.repositories.part_instance_repository import PartInstanceRepository
from src.infrastructure.db.repositories.sequences_repository import SequencesRepository
from src.infrastructure.db.repositories.work_orders_repository import WorkOrdersRepository
from src.infrastructure.db.repositories.user_repository import UserRepository

programs_repo = ProgramsRepository()
part_numbers_repo = PartNumbersRepository()
conveyors_repo = ConveyorsRepository()
history_repo = HistoryRepository()
part_instance_repo = PartInstanceRepository()
sequences_repo = SequencesRepository()
work_orders_repo = WorkOrdersRepository()
user_repo = UserRepository()

__all__ = [
    'programs_repo', 'part_numbers_repo', 'conveyors_repo',
    'history_repo', 'part_instance_repo', 'sequences_repo',
    'work_orders_repo', 'user_repo',
]
