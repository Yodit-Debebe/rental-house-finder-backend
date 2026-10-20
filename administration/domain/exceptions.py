class AdministrationError(Exception):
    """Base class for administration domain errors."""


class UserNotFound(AdministrationError):
    """No user account exists with the given identifier."""


class CannotModifySelf(AdministrationError):
    """An administrator may not change their own role or status."""


class InvalidRole(AdministrationError):
    """The requested role is not a valid platform role."""
