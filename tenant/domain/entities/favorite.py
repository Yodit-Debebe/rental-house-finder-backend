from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Favorite:
    tenant_id: UUID
    property_id: UUID
    id: UUID = field(default_factory=uuid4)
    saved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
