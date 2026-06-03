from src.infrastructure.db.repositories import (
    user_repo, programs_repo, part_numbers_repo, sequences_repo,
    work_orders_repo, conveyors_repo, part_instance_repo, history_repo,
)
from src.application.services.auth_service import AuthService
from src.application.services.program_service import ProgramService
from src.application.services.part_number_service import PartNumberService
from src.application.services.sequence_service import SequenceService
from src.application.services.work_order_service import WorkOrderService
from src.application.services.conveyor_service import ConveyorService
from src.application.services.part_tracking_service import PartTrackingService
from src.application.services.history_service import HistoryService

auth_service = AuthService(user_repo)
program_service = ProgramService(programs_repo)
part_number_service = PartNumberService(part_numbers_repo)
sequence_service = SequenceService(sequences_repo)
work_order_service = WorkOrderService(work_orders_repo)
conveyor_service = ConveyorService(conveyors_repo)
part_tracking_service = PartTrackingService(part_instance_repo)
history_service = HistoryService(history_repo)

__all__ = [
    'auth_service',
    'program_service',
    'part_number_service',
    'sequence_service',
    'work_order_service',
    'conveyor_service',
    'part_tracking_service',
    'history_service',
]
