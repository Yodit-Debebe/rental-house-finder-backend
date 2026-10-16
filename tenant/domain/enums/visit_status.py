from enum import Enum


class VisitRequestStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
