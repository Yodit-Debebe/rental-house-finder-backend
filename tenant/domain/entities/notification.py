from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from ..enums import NotificationType


@dataclass
class Notification:
    recipient_id: UUID
    notification_type: NotificationType
    title: str
    message: str
    id: UUID = field(default_factory=uuid4)
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Notification title cannot be empty.")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("Notification message cannot be empty.")
        self.title = self.title.strip()
        self.message = self.message.strip()

    def mark_as_read(self) -> None:
        self.is_read = True
        self.read_at = datetime.now(timezone.utc)

    def mark_as_unread(self) -> None:
        self.is_read = False
        self.read_at = None
