from dataclasses import dataclass

from property_management.domain.exceptions import InvalidProperty


@dataclass(frozen=True)
class Address:
    """A street address in a city, guaranteed to be non-empty."""

    street: str
    city: str

    def __post_init__(self):
        street = self.street.strip()
        city = self.city.strip()
        if not street:
            raise InvalidProperty("Street address must not be empty")
        if not city:
            raise InvalidProperty("City must not be empty")
        object.__setattr__(self, "street", street)
        object.__setattr__(self, "city", city)
