from dataclasses import dataclass
from decimal import Decimal

from property_management.domain.exceptions import InvalidProperty
from property_management.domain.value_objects import Address


@dataclass
class Property:
    """A rental property owned by a landlord. Free of Django and database code."""

    landlord_id: int
    title: str
    description: str
    address: Address
    price: Decimal
    bedrooms: int
    bathrooms: int
    is_available: bool = True
    id: int | None = None

    def __post_init__(self):
        self.title = self.title.strip()
        self.description = self.description.strip()
        self.price = Decimal(str(self.price))

        if not self.title:
            raise InvalidProperty("Property title must not be empty")
        if self.price < 0:
            raise InvalidProperty("Price must not be negative")
        if self.bedrooms < 0:
            raise InvalidProperty("Bedrooms must not be negative")
        if self.bathrooms < 0:
            raise InvalidProperty("Bathrooms must not be negative")
