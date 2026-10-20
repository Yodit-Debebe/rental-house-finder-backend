from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreatePropertyCommand:
    landlord_id: int
    title: str
    description: str
    address: str
    city: str
    price: Decimal
    bedrooms: int
    bathrooms: int
    is_available: bool = True
