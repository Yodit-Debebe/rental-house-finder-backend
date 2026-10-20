from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class UpdatePropertyCommand:
    """Only the provided fields are changed; None means "keep the current value"."""

    property_id: int
    landlord_id: int
    title: str | None = None
    description: str | None = None
    address: str | None = None
    city: str | None = None
    price: Decimal | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    is_available: bool | None = None
    amenity_ids: list[int] | None = None
