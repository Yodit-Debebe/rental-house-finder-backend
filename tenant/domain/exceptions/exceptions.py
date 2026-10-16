class DomainException(Exception):
    """Base exception for all tenant domain errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidBudgetRangeException(DomainException):
    """Raised when budget range values violate domain invariants."""
    pass


class InvalidVisitDateException(DomainException):
    """Raised when a requested visit date is in the past or invalid."""
    pass


class EmptyInquiryMessageException(DomainException):
    """Raised when an inquiry message is empty or exceeds character limits."""
    pass


class InvalidLocationPreferenceException(DomainException):
    """Raised when location preference is empty or invalid."""
    pass


class DuplicateFavoriteException(DomainException):
    """Raised when a tenant attempts to favorite an already favorited property."""
    pass


class DuplicateVisitRequestException(DomainException):
    """Raised when a tenant already has an active/pending visit request for a property."""
    pass


class DuplicateListingReportException(DomainException):
    """Raised when a tenant attempts to report the same listing multiple times."""
    pass


class TenantProfileNotFoundException(DomainException):
    """Raised when a tenant profile cannot be found."""
    pass


class PropertyNotAvailableException(DomainException):
    """Raised when attempting an action on an unavailable or unapproved property."""
    pass


class UnauthorizedTenantAccessException(DomainException):
    """Raised when a tenant attempts to access resources belonging to another tenant."""
    pass
