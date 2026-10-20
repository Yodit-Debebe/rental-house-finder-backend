class PropertyError(Exception):
    """Base class for property domain errors."""


class InvalidProperty(PropertyError):
    """The property data violates a domain rule."""


class PropertyNotFound(PropertyError):
    """No property exists with the given identifier."""


class NotPropertyOwner(PropertyError):
    """The acting user is not the landlord who owns the property."""
