from enum import Enum


class InquiryStatus(str, Enum):
    OPEN = "open"
    RESPONDED = "responded"
    CLOSED = "closed"
