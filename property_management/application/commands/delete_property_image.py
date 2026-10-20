from dataclasses import dataclass


@dataclass(frozen=True)
class DeletePropertyImageCommand:
    property_id: int
    image_id: int
    landlord_id: int
