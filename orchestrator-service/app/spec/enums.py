from enum import StrEnum


class SpecStatus(StrEnum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    DONE = "done"
    FAILED = "failed"