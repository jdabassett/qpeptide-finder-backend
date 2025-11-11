from enum import Enum as PyEnum


class DigestStatusEnum(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
