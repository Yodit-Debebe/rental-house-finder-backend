class DomainError(Exception):
    """Base class for violated business rules."""


class InvalidEmail(DomainError):
    def __init__(self, value: str):
        super().__init__(f"Invalid email address: {value!r}")
        self.value = value
