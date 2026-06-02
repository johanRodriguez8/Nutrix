from enum import Enum


class ConveyorStatus(str, Enum):
    EMPTY = 'EMPTY'
    OCCUPIED = 'OCCUPIED'
    DISABLED = 'DISABLED'
