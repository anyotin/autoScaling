from enum import IntEnum


class StateCode(IntEnum):
    PENDING = 0
    RUNNING = 16
    SHUTTING_DOWN = 32
    TERMINATED = 48
    STOPPING = 64
    STOPPED = 80
