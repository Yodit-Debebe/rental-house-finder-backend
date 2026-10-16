from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from ..enums import VisitRequestStatus
from ..value_objects import VisitDate


@dataclass
class VisitRequest:
    tenant_id: UUID
    property_id: UUID
    requested_date: VisitDate
    id: UUID = field(default_factory=uuid4)
    status: VisitRequestStatus = VisitRequestStatus.REQUESTED
    landlord_note: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def confirm(self, note: Optional[str] = None) -> None:
        self.status = VisitRequestStatus.CONFIRMED
        if note:
            self.landlord_note = note.strip()
        self.updated_at = datetime.now(timezone.utc)

    def decline(self, note: Optional[str] = None) -> None:
        self.status = VisitRequestStatus.DECLINED
        if note:
            self.landlord_note = note.strip()
        self.updated_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        self.status = VisitRequestStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        self.status = VisitRequestStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc)

    def is_pending(self) -> bool:
        return self.status == VisitRequestStatus.REQUESTED
