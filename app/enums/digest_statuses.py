from enum import Enum as PyEnum


class DigestStatusEnum(str, PyEnum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
