from enum import Enum


class NotificationType(str, Enum):
    INQUIRY_REPLY = "inquiry_reply"
    VISIT_UPDATE = "visit_update"
    PRICE_CHANGE = "price_change"
    AVAILABILITY_CHANGE = "availability_change"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
