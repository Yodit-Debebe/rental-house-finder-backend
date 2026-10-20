from dataclasses import dataclass

from property_management.domain.exceptions import InvalidAmenity


@dataclass(frozen=True)
class Amenity:
    """A feature a property can offer (e.g. parking, wifi)."""

    name: str
    id: int | None = None

    def __post_init__(self):
        name = self.name.strip()
        if not name:
            raise InvalidAmenity("Amenity name must not be empty")
        object.__setattr__(self, "name", name)
