class ApplicationError(Exception):
    """Base class for failures reported by use cases."""


class EmailAlreadyRegistered(ApplicationError):
    def __init__(self, email: str):
        super().__init__(f"Email is already registered: {email}")
        self.email = email


class InvalidCredentials(ApplicationError):
    def __init__(self):
        super().__init__("Invalid email or password.")
