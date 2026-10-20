import re
from dataclasses import dataclass
from enum import Enum

from identity.domain.exceptions import InvalidEmail

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    """An email address that cannot exist in an invalid state."""

    value: str

    def __post_init__(self):
        normalized = self.value.strip().lower()
        if not _EMAIL_PATTERN.fullmatch(normalized):
            raise InvalidEmail(self.value)
        object.__setattr__(self, "value", normalized)

    def __str__(self):
        return self.value


class Role(str, Enum):
    TENANT = "tenant"
    LANDLORD = "landlord"
    ADMIN = "admin"
