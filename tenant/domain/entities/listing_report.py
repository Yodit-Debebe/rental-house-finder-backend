from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from ..enums import ListingReportStatus


@dataclass
class ListingReport:
    tenant_id: UUID
    property_id: UUID
    reason: str
    id: UUID = field(default_factory=uuid4)
    status: ListingReportStatus = ListingReportStatus.SUBMITTED
    admin_notes: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("Report reason cannot be empty.")
        self.reason = self.reason.strip()

    def mark_under_review(self, notes: Optional[str] = None) -> None:
        self.status = ListingReportStatus.UNDER_REVIEW
        if notes:
            self.admin_notes = notes.strip()
        self.updated_at = datetime.now(timezone.utc)

    def resolve(self, notes: Optional[str] = None) -> None:
        self.status = ListingReportStatus.RESOLVED
        if notes:
            self.admin_notes = notes.strip()
        self.updated_at = datetime.now(timezone.utc)

    def dismiss(self, notes: Optional[str] = None) -> None:
        self.status = ListingReportStatus.DISMISSED
        if notes:
            self.admin_notes = notes.strip()
        self.updated_at = datetime.now(timezone.utc)
