from enum import StrEnum


class CrashType(StrEnum):
    SEGFAULT = "segfault"
    BUS_ERROR = "bus_error"
    ABORT = "abort"
    TIMEOUT = "timeout"
    HEAP_OVERFLOW = "heap_overflow"
    STACK_OVERFLOW = "stack_overflow"
    UNKNOWN = "unknown"
