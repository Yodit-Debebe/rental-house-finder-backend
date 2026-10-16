from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from ..enums import InquiryStatus
from ..value_objects import InquiryMessage


@dataclass
class Inquiry:
    tenant_id: UUID
    property_id: UUID
    landlord_id: UUID
    message: InquiryMessage
    id: UUID = field(default_factory=uuid4)
    status: InquiryStatus = InquiryStatus.OPEN
    landlord_reply: Optional[str] = None
    replied_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def record_reply(self, reply: str) -> None:
        clean_reply = reply.strip() if reply else ""
        if not clean_reply:
            raise ValueError("Reply text cannot be empty.")
        self.landlord_reply = clean_reply
        self.status = InquiryStatus.RESPONDED
        self.replied_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def close(self) -> None:
        self.status = InquiryStatus.CLOSED
        self.updated_at = datetime.now(timezone.utc)
