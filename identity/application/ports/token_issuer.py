from abc import ABC, abstractmethod

from identity.domain.entities import User


class TokenIssuer(ABC):
    """Outbound port: issues an authentication token for a user.

    Today this is implemented with DRF tokens; a Keycloak adapter can replace
    it later without changing the use cases.
    """

    @abstractmethod
    def issue(self, user: User) -> str:
        ...
