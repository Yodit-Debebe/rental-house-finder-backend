from dataclasses import dataclass


@dataclass(frozen=True)
class DeletePropertyCommand:
    property_id: int
    landlord_id: int
