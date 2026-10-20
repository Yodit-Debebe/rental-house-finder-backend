from dataclasses import dataclass


@dataclass(frozen=True)
class GetPropertyQuery:
    property_id: int
    landlord_id: int
