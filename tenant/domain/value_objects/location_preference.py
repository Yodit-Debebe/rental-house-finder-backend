from dataclasses import dataclass
from typing import Optional
from ..exceptions import InvalidLocationPreferenceException


@dataclass(frozen=True)
class LocationPreference:
    city: str
    area: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.city, str) or not self.city.strip():
            raise InvalidLocationPreferenceException("City cannot be empty.")

        clean_city = self.city.strip()
        clean_area = self.area.strip() if self.area and isinstance(self.area, str) and self.area.strip() else None

        object.__setattr__(self, "city", clean_city)
        object.__setattr__(self, "area", clean_area)

    def matches(self, other_city: str, other_area: Optional[str] = None) -> bool:
        if self.city.lower() != other_city.strip().lower():
            return False
        if self.area is not None and other_area is not None:
            return self.area.lower() in other_area.strip().lower()
        return True

    def __str__(self) -> str:
        if self.area:
            return f"{self.area}, {self.city}"
        return self.city
