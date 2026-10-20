from dataclasses import dataclass


@dataclass(frozen=True)
class UploadPropertyImageCommand:
    property_id: int
    landlord_id: int
    file_name: str
    content: bytes
    caption: str = ""
    is_cover: bool = False
