from rest_framework.authtoken.models import Token

from identity.application.ports import TokenIssuer
from identity.domain.entities import User


class DRFTokenIssuer(TokenIssuer):
    """Implements the TokenIssuer port with DRF's built-in token table."""

    def issue(self, user: User) -> str:
        token, _created = Token.objects.get_or_create(user_id=user.id)
        return token.key
