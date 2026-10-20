from dataclasses import dataclass


@dataclass(frozen=True)
class ListLandlordPropertiesQuery:
    landlord_id: int
