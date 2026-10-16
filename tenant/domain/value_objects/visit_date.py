from dataclasses import dataclass
from datetime import datetime, timezone
from ..exceptions import InvalidVisitDateException


@dataclass(frozen=True)
class VisitDate:
    value: datetime

    def __post_init__(self):
        if not isinstance(self.value, datetime):
            raise InvalidVisitDateException("Visit date must be a valid datetime instance.")

        # Normalize to UTC for comparison
        now = datetime.now(timezone.utc)
        target = self.value if self.value.tzinfo is not None else self.value.replace(tzinfo=timezone.utc)

        if target <= now:
            raise InvalidVisitDateException("Requested visit date must be in the future.")

        object.__setattr__(self, "value", target)

    def to_iso_format(self) -> str:
        return self.value.isoformat()
