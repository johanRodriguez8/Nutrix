from enum import Enum


class PartState(str, Enum):
    IDLE     = 'IDLE'
    READY    = 'READY'
    RUNNING  = 'RUNNING'
    DRYING   = 'DRYING'
    WAITING  = 'WAITING'
    ALARM    = 'ALARM'
    DONE     = 'DONE'
    COMPLETE = 'COMPLETE'
