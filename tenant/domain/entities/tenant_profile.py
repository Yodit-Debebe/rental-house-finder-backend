from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from ..value_objects import BudgetRange, LocationPreference


@dataclass
class TenantProfile:
    user_id: UUID
    id: UUID = field(default_factory=uuid4)
    preferred_location: Optional[LocationPreference] = None
    budget_range: Optional[BudgetRange] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_preferences(
        self,
        preferred_location: Optional[LocationPreference] = None,
        budget_range: Optional[BudgetRange] = None,
    ) -> None:
        if preferred_location is not None:
            self.preferred_location = preferred_location
        if budget_range is not None:
            self.budget_range = budget_range
        self.updated_at = datetime.now(timezone.utc)

    def set_budget(self, min_price: Optional[Decimal], max_price: Optional[Decimal]) -> None:
        self.budget_range = BudgetRange(min_price=min_price, max_price=max_price)
        self.updated_at = datetime.now(timezone.utc)

    def set_location(self, city: str, area: Optional[str] = None) -> None:
        self.preferred_location = LocationPreference(city=city, area=area)
        self.updated_at = datetime.now(timezone.utc)
