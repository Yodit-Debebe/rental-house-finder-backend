from dataclasses import dataclass


@dataclass(frozen=True)
class PropertyImage:
    """A photo attached to a property. The URL is produced by infrastructure."""

    property_id: int
    url: str
    caption: str = ""
    is_cover: bool = False
    id: int | None = None
