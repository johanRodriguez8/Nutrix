from enum import Enum


class PartState(str, Enum):
    IDLE = 'IDLE'
    RUNNING = 'RUNNING'
    WAITING = 'WAITING'
    COMPLETE = 'COMPLETE'
